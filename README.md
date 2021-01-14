# Serverless LoR Match Scraper

This project contains infrastructure code to create a serverless Legends of Runeterra match scraper on AWS using CDK.

Currently this code base creates the following resources when deployed:

### State Machine:
This state machine is the main "brain" of this project. This state machine contains logic that will query a list of players, then for each player will:

1. Pull match history for the player.
2. Check which matches have been ran in the past.
3. Query match data for each match to be processed.
4. Write the match data to a Match table.
5. When all matches have been written, update player in database with new win loss totals.

#### Flow chart of the state machine:
![alt text](https://lor-match-scraper-bucket.s3-us-west-2.amazonaws.com/LoRServerlessMatchScraperDiagram.png)

 ### Lambda Functions:
 7 different Lambda functions are used to perform the logic in the state machine. These Lambdas are written in Python3.8 and use a few custom layers to achieve their functionality ([requests](https://requests.readthedocs.io/en/master/) and [lor-deckcodes](https://github.com/Rafalonso/LoRDeckCodesPython))

### EventBridge Rule:
An EventBridge Rule is created to schedule execution of the state machine. Currently in this project it set to execute every 30 minutes. 

### DynamoDB Tables (x2):
Two DynamoDB Tables are used, LoR-Player-Table and LoR-Match-Table. 
* LoR-Player-Table is used to store all players the system will track. Currently players must be manually entered. Player entries lust have the following entries to run properly:
    * player_uuid (S): The players uuid assigned by riot. (Primary Key)
    * region (S): Region player is located in.
    * match_cache (L): Used to store matches last checked. Set as blank list.
    * wins (N): Number of player wins. Set to 0.
    * losses (N): Number of player losses. Set to 0.
* LoR-Match-Table is used to store match data. Each match checked will be written to this table.
    * match_id: The matches unique id. (Primary Key)
    * date: Time match was played in epoch. (Sort Key)
    * mode: Game type of match.
    * type: If constructed game mode, either standard or ranked.
    * turn_count: Number of turns match took.
    * player1_uuid: Starting player's uuid.
    * player2_uuid: Second acting player's uuid.
    * player1_deck: Player 1's deck code.
    * player2_deck: Player 2's deck code.
    * player1_factions: Factions of player 1's deck
    * player2_factions: Factions of player 2's deck
    * player1_champions: Champions in player 1's deck
    * player2_champions: Champions in player 2's deck
    * winner: Uuid of winning player.
    * loser: Uuid of losing player.

#### CDK Commands
*  `npm run build` compile typescript to js

*  `npm run watch` watch for changes and compile

*  `npm run test` perform the jest unit tests

*  `cdk deploy` deploy this stack to your default AWS account/region

*  `cdk diff` compare deployed stack with current state

*  `cdk synth` emits the synthesized CloudFormation template