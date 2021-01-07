#!/usr/bin/env node
import 'source-map-support/register';
import {App} from 'monocdk';
import { DynamoStack } from '../lib/dynamoStack';

const app = new App();
new DynamoStack(app, 'GameAgentCdkStack');
