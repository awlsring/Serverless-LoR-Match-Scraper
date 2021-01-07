import {Stack, StackProps, Construct, Duration} from 'monocdk';
import {RestApi, LambdaIntegration, PassthroughBehavior} from 'monocdk/aws-apigateway'
import {Function, Runtime, Code, Tracing, } from 'monocdk/aws-lambda'
import {Role, ServicePrincipal} from 'monocdk/aws-iam'

export class ApiGatewayStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const api = new RestApi(this, "WebsiteGateway");

    // Creates Generic Page Function
    const dataPoster = new Function(this, 'dataPoster', {
        runtime: Runtime.PYTHON_3_8,
        handler: 'post-results.lambda_handler',
        code: Code.fromAsset('Handlers'),
        memorySize: 512,
        tracing: Tracing.ACTIVE,
        timeout: Duration.seconds(5),
        functionName: 'Post-Results',
        role: new Role(this, 'Post-Results', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            roleName: 'Lambda-Post-Results'
        })
      });

    // Creates Get Method to call Lambda Function that assembles and returns the web page
    api.root.addMethod('Get', new LambdaIntegration(dataPoster, {
      proxy: false,
      requestTemplates: {
        'application/json': `{ "Page": "home.html" }`,
      },
      integrationResponses: [{
        statusCode: '200',
        responseTemplates: {
          'text/html': "$input.path('$')"
        },
        responseParameters: {
          "method.response.header.Content-Type": "'text/html'"
        }
      }]
    }),{
      methodResponses: [{
        statusCode: '200',
        responseParameters: {
          "method.response.header.Content-Type": true
        }
      }]
    });

    // Creates resource for posts
    const post = website.root.addResource('posts');

    post.addMethod('Get', new LambdaIntegration(pageHandler, {
      proxy: false,
      passthroughBehavior: PassthroughBehavior.NEVER,
      requestTemplates: {
          'application/json': `{ 
            "PostID": "$input.params('post')",
            "Page": "post.html"
          }`,
      },
      integrationResponses: [{
        statusCode: '200',
        responseTemplates: {
          'text/html': "$input.path('$')"
        },
        responseParameters: {
          "method.response.header.Content-Type": "'text/html'"
        }
      }]
    }),{
      methodResponses: [{
        statusCode: '200',
        responseParameters: {
          "method.response.header.Content-Type": true
        }
      }]
    });

  }
}