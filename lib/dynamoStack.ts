import {Stack, StackProps, Construct} from 'monocdk';
import {Table, AttributeType} from 'monocdk/aws-dynamodb'

export class DynamoStack extends Stack {

  public dynamoTables: Map<string, string> = new Map;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

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

  }
}
