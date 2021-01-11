import {Stack, StackProps, Construct} from 'monocdk';
import {Table, AttributeType} from 'monocdk/aws-dynamodb'

export class DynamoStack extends Stack {

  public dynamoTables: Map<string, string>

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const lorMatchesTable = new Table(this, "LoR-Matches-Table", {
      partitionKey: { name: 'MatchID', type: AttributeType.STRING },
      sortKey: {name: 'Date', type: AttributeType.NUMBER},
      tableName: "LoR-Matches-Table",
    });

    const lorPlayersTable = new Table(this, "LoR-Players-Table", {
      partitionKey: { name: 'PUUID', type: AttributeType.STRING },
      tableName: "LoR-Player-Table",
    });

    this.dynamoTables.set("Matches", lorMatchesTable.tableArn)
    this.dynamoTables.set("Players", lorPlayersTable.tableArn)

  }
}
