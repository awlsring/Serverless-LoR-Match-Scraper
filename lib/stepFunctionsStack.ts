import {Stack, StackProps, Construct, Duration} from 'monocdk';
import {StateMachine, Choice, Condition, Pass, Wait, WaitTime} from 'monocdk/aws-stepfunctions'
import {LambdaInvoke} from 'monocdk/aws-stepfunctions-tasks'
import {Function, Runtime, Code, Tracing} from 'monocdk/aws-lambda'
import {Role, ServicePrincipal, PolicyStatement} from 'monocdk/aws-iam'

export class StepFunctionStack extends Stack {
  constructor(scope: Construct, id: string, tables: Map<string, string>, props?: StackProps) {
    super(scope, id, props);
    
    // Lambda Functions for Step Functions
    const queryPlayersListLambda = new Function(this, 'Query-Player-List-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'query-player-list.lambda_handler',
      code: Code.fromAsset('Handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Query-Player-List',
      role: new Role(this, 'LoR-Query-Player-List-Role', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Query-Player-Role'
      })
    })

    // Pass dynamo arn to this section
    queryPlayersListLambda.addToRolePolicy(new PolicyStatement( {
      resources: [ <string>tables.get('Players') ],
      actions: [ 'dynamodb:Scan' ]
    }))

    const getPlayerMatchesLambda = new Function(this, 'Get-Player-Matches-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'get-player-matches.lambda_handler',
      code: Code.fromAsset('Handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Query-Player-List',
      role: new Role(this, 'LoR-Get-Player-Matches', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Get-Player-Matches-Role'
      })
    })

    const compareMatchesLambda = new Function(this, 'Compare-Matches-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'compare-match.lambda_handler',
      code: Code.fromAsset('Handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Compare-Match',
      role: new Role(this, 'LoR-Compare-Role', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Compare-Match-Role'
      })
    })

    const getMatchLambda = new Function(this, 'Get-Match-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'get-match.lambda_handler',
      code: Code.fromAsset('Handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Get-Match-List',
      role: new Role(this, 'LoR-Get-Match', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Get-Match-Role'
      })
    })

    const writeMatchDataLambda = new Function(this, 'Write-Match-Data-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'write-match-data.lambda_handler',
      code: Code.fromAsset('Handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Write-Match-Data',
      role: new Role(this, 'LoR-Write-Match-Data', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Write-Match-Data-Role'
      })
    })

    // Pass dynamo arn to this section
    writeMatchDataLambda.addToRolePolicy(new PolicyStatement( {
      resources: [ <string>tables.get('Matches') ],
      actions: [ 'dynamodb:PutItem' ]
    }))


    // Step Definitions 

    const queryPlayerListStep = new LambdaInvoke(this, 'Query-Player-List-Step', {
      lambdaFunction: queryPlayersListLambda,
      outputPath: "$.event",
    });

    const forPlayerInListStep = new Choice(this, 'For-Player-In-List', {
      inputPath: "$.event",
      outputPath: "$.event",
    })

    const finishPlayerLoop = new Pass(this, 'Finish-Player-Loop')

    const getPlayerMatchesStep = new LambdaInvoke(this, 'Get-Player-Match-Step', {
      lambdaFunction: getPlayerMatchesLambda,
      inputPath: "$.event",
      outputPath: "$.event",
    });
    
    const checkForRiotBackoffMatchList = new Choice(this, 'Check-For-Riot-Backoff-Step', {
      inputPath: "$.event",
      outputPath: "$.event",
    })

    const waitForBackoffDurationMatchList = new Wait(this, 'Wait-For-Backoff-Duration', {
      time: WaitTime.timestampPath('$.event.headers.Retry-After ')
    })

    const compareMatchesStep = new LambdaInvoke(this, 'Compare-Match-Step', {
      lambdaFunction: compareMatchesLambda,
      inputPath: "$.event",
      outputPath: "$.event",
    });

    const forMatchNotInCache = new Choice(this, 'For-Match-Not-In-Cache', {
      inputPath: "$.event",
      outputPath: "$.event",
    })

    const getMatchStep = new LambdaInvoke(this, 'Get-Match-Step', {
      lambdaFunction: getMatchLambda,
      inputPath: "$.event",
      outputPath: "$.event",
    });

    const checkForRiotBackoffMatch = new Choice(this, 'Check-For-Riot-Backoff-Step', {
      inputPath: "$.event",
      outputPath: "$.event",
    })

    const waitForBackoffDurationMatch = new Wait(this, 'Wait-For-Backoff-Duration', {
      time: WaitTime.timestampPath('$.event.headers.Retry-After ')
    })
    
    const writeMatchDataStep = new LambdaInvoke(this, 'Write-Match-Data-Step', {
      lambdaFunction: writeMatchDataLambda,
      inputPath: "$.event",
      outputPath: "$.event",
    });
    
    // Step Order Definition
    const stepDefinition = queryPlayerListStep
      .next(forPlayerInListStep)
        forPlayerInListStep.when(Condition.booleanEquals('$.event.all_players_checked?', false), getPlayerMatchesStep)
        forPlayerInListStep.when(Condition.booleanEquals('$.event.all_players_checked?', true), finishPlayerLoop)

      getPlayerMatchesStep.next(checkForRiotBackoffMatchList)
        checkForRiotBackoffMatchList.when(Condition.numberEquals('$.event.status_code', 200), compareMatchesStep)
        checkForRiotBackoffMatchList.when(Condition.numberEquals('$.event.status_code', 429), waitForBackoffDurationMatchList)

      waitForBackoffDurationMatchList.next(getPlayerMatchesStep)

      compareMatchesStep.next(forMatchNotInCache)
        forMatchNotInCache.when(Condition.booleanEquals('$.event.all_matches_checked', true), forPlayerInListStep)
        forMatchNotInCache.when(Condition.booleanEquals('$.event.all_matches_checked', false), getMatchStep)

      getMatchStep.next(checkForRiotBackoffMatch)
        checkForRiotBackoffMatch.when(Condition.numberEquals('$.event.status_code', 200), writeMatchDataStep)
        checkForRiotBackoffMatch.when(Condition.numberEquals('$.event.status_code', 429), waitForBackoffDurationMatch)

      waitForBackoffDurationMatch.next(getMatchStep)

      writeMatchDataStep.next(forMatchNotInCache)

    new StateMachine(this, 'LoR-State-Machine', {
      definition: stepDefinition,
      stateMachineName: "LoR-Match-Processor"
    })

  }
}
