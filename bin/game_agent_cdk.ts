#!/usr/bin/env node
import { App } from 'monocdk';
import { DynamoStack } from '../lib/dynamoStack';
import { StepFunctionStack } from '../lib/stepFunctionsStack';

const app = new App();
const dynamoStack = new DynamoStack(app, 'Dynamo-Stack');
new StepFunctionStack(
    app,
    'Step-Functions-Stack',
    dynamoStack.dynamoTables,
    )
