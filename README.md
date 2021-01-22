# Serverless LoR Match Scraper

This project contains infrastructure code to create a serverless Legends of Runeterra match scraper on AWS using CDK.

[There is an accompanying React package that can be found here](https://github.com/Awlsring/LoR-Match-Scraper-Front-End)

Currently this code base creates the following resources when deployed:

### State Machine:
This state machine is the main "brain" of this project. This state machine contains logic that will query a list of players, then for each player will:

1. Pull match history for the player.
2. Check which matches have been ran in the past.
3. Query match data for each match to be processed.
4. Write the match data to a Match table.
5. When all matches have been written for a player, update player in database with new win/loss totals, match history, and deck history.
6. When all players have ran, write all deck data from matches processed to database.

#### Flow chart of the state machine:
![alt text](https://lor-match-scraper-bucket.s3-us-west-2.amazonaws.com/stepfunctions_graph.png)

### API Gateway:
An API Gateway is used to expose endpoints to convey information about the players, matches, and decks that has been gathered from scraping match history. Currently this is only configured to give information to the frontend and isnt setup in any public consumer sort of way.

### Lambda Functions:
6 different Lambda functions are used to perform the logic in the state machine. These Lambdas are written in Python3.8 and use a few custom layers to achieve their functionality ([requests](https://requests.readthedocs.io/en/master/) and [lor-deckcodes](https://github.com/Rafalonso/LoRDeckCodesPython))

2 different Lambda functions are used by the api gateway to query and communicate informations to users.

### EventBridge Rule:
An EventBridge Rule is created to schedule execution of the state machine. Currently in this project it is set to execute every hour. 

### DynamoDB Tables:
Several DynamoDB Tables are used. 3 to convey player information, and 2 to store more genreal information.
* LoR-Player-Info-Table - used to store general player data.
    * player_uuid (S): The players uuid assigned by riot. (Primary Key)
    * last_scanned (N): Last time player entry was updated by system.
    * player_name (S): Player's in game name.
    * player_tag (S): Player's region tag.
    * region (S): Region player is located in.
    * match_cache (L): Used to store matches last checked.
    * wins (N): Number of player wins.
    * losses (N): Number of player losses.

* LoR-Player-Matches-Table - used to store a list of all matches a player has played in.
    * player_uuid (S): The players uuid assigned by riot. (Primary Key)
    * matches (SS): All matches a player has played.

* LoR-Player-Decks-Table - used to store information on all decks a player has played. Every key other than player_uuid is variable, and is named after the legends the deck is made from.
    * player_uuid (S): The players uuid assigned by riot. (Primary Key)
    * {Deck Played} (M): Contains a map with variants of the deck, along with total wins and losses.
    
* LoR-Matches-Table - used to store match data. Each match checked will be written to this table.
    * match_id (S): The matches unique id. (Primary Key)
    * date (N): Time match was played in epoch. (Sort Key)
    * type (S): Standard or ranked.
    * turn_count (N): Number of turns match took.
    * player1 (M): Map tracking player1 data. Contains...
        * deckcode (S): Deck's code.
        * factions (L): Deck's factions.
        * legends (S): Legends in the deck. Used as primary key for deck tables.
        * uuid (S): Players UUID
    * player2 (M): Map tracking player2 data. Contains same info as player1.
    * winner (S): Uuid of winning player.
    * loser (S): Uuid of losing player.

* LoR-Decks-Table - used to store information about all decks that have been played.
    * legends (S): Legends in the deck. combined into string formatted like "deck_{legend}"
    * variants (SS): Set of all variants of the deck played.
    * match_ups (M): Map of decks that have played against this deck.
        * {deck_name} (M): Map containing wins and losses against this deck
            * wins (N): Total wins.
            * losses (N): Total losses.
    * wins (N): Overall wins deck has had.
    * losses (N): Overall losses deck has had.


### S3 Bucket & Bucket Deployment
An S3 bucket is used to host the wesbsite. The build for the react projet is targeted by the bucket deployment is sent to the bucket eveytime `cdk deploy` targotting the resource stack is run. [The webpage this creates can be accessed here.](https://lor-match-tracker-react-bucket.s3-us-west-2.amazonaws.com/index.html)

#### CDK Commands
*  `npm run build` compile typescript to js
*  `npm run watch` watch for changes and compile
*  `npm run test` perform the jest unit tests
*  `cdk deploy` deploy this stack to your default AWS account/region
*  `cdk diff` compare deployed stack with current state
*  `cdk synth` emits the synthesized CloudFormation template