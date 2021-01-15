#!/usr/bin/env node
import { App } from 'monocdk';
import { DynamoStack } from '../lib/dynamoStack';
import { StepFunctionStack } from '../lib/stepFunctionsStack';
import { ResourcesStack } from '../lib/resourcesStack'
import { ApiGatewayStack } from '../lib/apiGatewayStack'

const app = new App();
const resourcesStack = new ResourcesStack(app, 'Resources-Stack')
const dynamoStack = new DynamoStack(app, 'Dynamo-Stack');
const apiGatewayStack = new ApiGatewayStack(
    app,
    'Api-Gateway-Stack',
    dynamoStack.dynamoTables,
    resourcesStack.lambdaLayers
)
new StepFunctionStack(
    app,
    'Step-Functions-Stack',
    dynamoStack.dynamoTables,
    resourcesStack.lambdaLayers
)
