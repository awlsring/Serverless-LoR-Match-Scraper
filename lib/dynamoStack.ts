import {Stack, StackProps, Construct} from 'monocdk';
import {Table, AttributeType} from 'monocdk/aws-dynamodb'

export class DynamoStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const lorTable = new Table(this, "LoR-Wins-Table", {
      partitionKey: { name: 'Match_Id', type: AttributeType.STRING },
      sortKey: {name: 'Match_Date', type: AttributeType.NUMBER},
      tableName: "LoR-Wins-Table",
  });
  }
}
