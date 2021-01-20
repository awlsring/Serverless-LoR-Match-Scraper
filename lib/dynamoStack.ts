import {Stack, StackProps, Construct} from 'monocdk';
import {Table, AttributeType} from 'monocdk/aws-dynamodb'

export class DynamoStack extends Stack {

  public dynamoTables: Map<string, string> = new Map;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Following two are unused, waiting untill new setup works to remove
    const lorMatchesTable = new Table(this, "LoR-Match-Table", {
      partitionKey: { name: 'match_id', type: AttributeType.STRING },
      sortKey: {name: 'date', type: AttributeType.NUMBER},
      tableName: "LoR-Match-Table",
    });

    const lorPlayersTable = new Table(this, "LoR-Players-Table", {
      partitionKey: { name: 'player_uuid', type: AttributeType.STRING },
      tableName: "LoR-Player-Table",
    });

    this.dynamoTables.set("Matches", lorMatchesTable.tableArn)
    this.dynamoTables.set("Players", lorPlayersTable.tableArn)

    // Player Tables    
    const playerInfo = new Table(this, "LoR-Player-Info-Table", {
      partitionKey: { name: 'player_uuid', type: AttributeType.STRING },
      sortKey: {name: 'last_scanned', type: AttributeType.NUMBER},
      tableName: "LoR-Player-Info-Table",
    });

    const playerDecks = new Table(this, "LoR-Player-Decks-Table", {
      partitionKey: { name: 'player_uuid', type: AttributeType.STRING },
      tableName: "LoR-Player-Decks-Table",
    });

    const playerMatches = new Table(this, "LoR-Player-Matches-Table", {
      partitionKey: { name: 'player_uuid', type: AttributeType.STRING },
      tableName: "LoR-Player-Matches-Table",
    });

    // Deck Table
    const decks = new Table(this, "LoR-Decks-Table", {
      partitionKey: { name: 'legends', type: AttributeType.STRING },
      tableName: "LoR-Decks-Table",
    });

    // Season Metadata Table
    const metadata = new Table(this, "LoR-Season-Metadata-Table", {
      partitionKey: { name: 'status', type: AttributeType.STRING },
      tableName: "LoR-Season-Metadata-Table",
    });

    // Match Table
    const matches = new Table(this, "LoR-Matches-Table", {
      partitionKey: { name: 'match_id', type: AttributeType.STRING },
      tableName: "LoR-Matches-Table",
    });

    this.dynamoTables.set("Player-Info", lorMatchesTable.tableArn)
    this.dynamoTables.set("Player-Decks", lorPlayersTable.tableArn)
    this.dynamoTables.set("Player-Matches", lorPlayersTable.tableArn)
    this.dynamoTables.set("Decks", lorPlayersTable.tableArn)
    this.dynamoTables.set("Metadata", lorPlayersTable.tableArn)
    this.dynamoTables.set("Matches", lorPlayersTable.tableArn)

  }
}