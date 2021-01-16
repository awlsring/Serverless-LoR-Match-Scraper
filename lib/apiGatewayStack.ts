import {Stack, StackProps, Construct, Duration} from 'monocdk';
import {RestApi, LambdaIntegration, PassthroughBehavior} from 'monocdk/aws-apigateway'
import {Function, Runtime, Tracing, Code, LayerVersion} from 'monocdk/aws-lambda'
import {Role, ServicePrincipal, PolicyStatement} from 'monocdk/aws-iam'

export class ApiGatewayStack extends Stack {
    constructor(scope: Construct, id: string, tables: Map<string, string>, layers: Map<string, LayerVersion>, props?: StackProps) {
        super(scope, id, props);

        const addPlayerFunction = new Function(this, 'LoR-Add-Player', {
            runtime: Runtime.PYTHON_3_8,
            layers: [ <LayerVersion>layers.get('requests') ],
            handler: 'add-player-to-list.lambda_handler',
            code: Code.fromAsset('lib/handlers/add-player-to-list'),
            memorySize: 128,
            tracing: Tracing.ACTIVE,
            timeout: Duration.seconds(5),
            functionName: 'LoR-Add-Player-To-List',
            role: new Role(this, 'LoR-Add-Player-To-List', {
              assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
              roleName: 'LoR-Add-Player-To-List'
            })
          })

          addPlayerFunction.addToRolePolicy(new PolicyStatement( {
        resources: [ "arn:aws:secretsmanager:us-west-2:742762521158:secret:Riot-API-Key-k2axBv" ],
        actions: [ 'secretsmanager:DescribeSecret', 'secretsmanager:GetSecretValue' ]
        }))

        addPlayerFunction.addToRolePolicy(new PolicyStatement( {
        resources: [ <string>tables.get('Players') ],
        actions: [ 'dynamodb:PutItem' ]
        }))

        const api = new RestApi(this, "LoR-Api")

        const addPlayer = api.root.addResource('AddPlayer')

        addPlayer.addMethod('Get', new LambdaIntegration(addPlayerFunction, {
            proxy: false,
            passthroughBehavior: PassthroughBehavior.NEVER,
            requestTemplates: {
                'application/json': `{ 
                    "username": "$input.params('username')",
                    "region": "$input.params('region')"
                }`,
            },
            integrationResponses: [{
                statusCode: '200',
                responseParameters: {
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET'",
                    "method.response.header.Access-Control-Allow-Origin": "'*'"
                  },
            }]}), {
            methodResponses: [{ 
                statusCode: '200',
                responseParameters: {
                    'method.response.header.Access-Control-Allow-Headers': true,
                    'method.response.header.Access-Control-Allow-Methods': true,
                    'method.response.header.Access-Control-Allow-Credentials': true,
                    'method.response.header.Access-Control-Allow-Origin': true,
                },
            }]
        })

    }
}