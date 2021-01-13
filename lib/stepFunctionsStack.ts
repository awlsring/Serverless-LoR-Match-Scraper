import {Stack, StackProps, Construct, Duration} from 'monocdk';
import {StateMachine, Choice, Condition, Pass, Wait, WaitTime} from 'monocdk/aws-stepfunctions'
import {LambdaInvoke} from 'monocdk/aws-stepfunctions-tasks'
import {Function, Runtime, Code, Tracing, LayerVersion} from 'monocdk/aws-lambda'
import {Role, ServicePrincipal, PolicyStatement} from 'monocdk/aws-iam'
import {Rule, Schedule} from 'monocdk/aws-events'
import {SfnStateMachine} from 'monocdk/aws-events-targets'

export class StepFunctionStack extends Stack {
  constructor(scope: Construct, id: string, tables: Map<string, string>, props?: StackProps) {
    super(scope, id, props);
    
    // Requests Layer
    const requestsLayer = new LayerVersion(this, "Requests-Layer", {
      code: Code.fromAsset('lib/handlers/lib/requests/requests.zip'),
      compatibleRuntimes: [ Runtime.PYTHON_3_8 ] ,
      description: "Lambda Layer for Requests",
      layerVersionName: "LoR-Requests"
    })

    // Lambda Functions for Step Functions
    const queryPlayersListLambda = new Function(this, 'Query-Player-List-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'query-player-list.lambda_handler',
      code: Code.fromAsset('lib/handlers'),
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
      layers: [ requestsLayer ],
      handler: 'get-player-matches.lambda_handler',
      code: Code.fromAsset('lib/handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Player-Matches',
      role: new Role(this, 'LoR-Player-Matches', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Get-Player-Matches-Role'
      })
    })

    const compareMatchesLambda = new Function(this, 'Compare-Matches-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'compare-matches.lambda_handler',
      code: Code.fromAsset('lib/handlers'),
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
      layers: [ requestsLayer ],
      handler: 'get-match.lambda_handler',
      code: Code.fromAsset('lib/handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Get-Match-List',
      role: new Role(this, 'LoR-Get-Match', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Get-Match-Role'
      })
    })

    const failMatchLambda = new Function(this, 'Fail-Match-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'fail-match.lambda_handler',
      code: Code.fromAsset('lib/handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Fail-Match',
      role: new Role(this, 'LoR-Fail-Match', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Fail-Match'
      })
    })

    const writeMatchDataLambda = new Function(this, 'Write-Match-Data-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'write-match-data.lambda_handler',
      code: Code.fromAsset('lib/handlers'),
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

    const writePlayerDataLambda = new Function(this, 'Write-Player-Data-Function', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'write-player-data.lambda_handler',
      code: Code.fromAsset('lib/handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'LoR-Write-Player-Data',
      role: new Role(this, 'LoR-Write-Player-Data', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'LoR-Write-Player-Data-Role'
      })
    })

    // Pass dynamo arn to this section
    writePlayerDataLambda.addToRolePolicy(new PolicyStatement( {
      resources: [ <string>tables.get('Players') ],
      actions: [ 'dynamodb:UpdateItem' ]
    }))

    // Step Definitions 
    const queryPlayerListStep = new LambdaInvoke(this, 'Query-Player-List-Step', {
      lambdaFunction: queryPlayersListLambda,
    });

    const forPlayerInListStep = new Choice(this, 'For-Player-In-List')

    const finishPlayerLoop = new Pass(this, 'Finish-Player-Loop')

    const getPlayerMatchesStep = new LambdaInvoke(this, 'Get-Player-Match-Step', {
      lambdaFunction: getPlayerMatchesLambda,
    });
    
    const checkForRiotBackoffMatchList = new Choice(this, 'Check-For-Riot-Backoff-Match-List-Step')

    const waitForBackoffDurationMatchList = new Wait(this, 'Wait-For-Backoff-Duration-Match-List-Step', {
      time: WaitTime.timestampPath('$.Payload.match_result.retry_after')
    })

    const compareMatchesStep = new LambdaInvoke(this, 'Compare-Match-Step', {
      lambdaFunction: compareMatchesLambda,
    });

    const forMatchNotInCache = new Choice(this, 'For-Match-Not-In-Cache')

    const getMatchStep = new LambdaInvoke(this, 'Get-Match-Step', {
      lambdaFunction: getMatchLambda,
    });

    const failMatchStep = new LambdaInvoke(this, 'Fail-Match-Step', {
      lambdaFunction: failMatchLambda,
    });

    const checkForRiotBackoffMatch = new Choice(this, 'Check-For-Riot-Backoff-Match-Step')

    const waitForBackoffDurationMatch = new Wait(this, 'Wait-For-Backoff-Duration-Match-Step', {
      time: WaitTime.timestampPath('$.Payload.current_player.current_match.retry_after')
    })
    
    const writeMatchDataStep = new LambdaInvoke(this, 'Write-Match-Data-Step', {
      lambdaFunction: writeMatchDataLambda,
    });

    const writeMatchPlayerStep = new LambdaInvoke(this, 'Write-Player-Data-Step', {
      lambdaFunction: writePlayerDataLambda,
    });
    
    // Step Order Definition
    const stepDefinition = queryPlayerListStep
      .next(forPlayerInListStep)
        forPlayerInListStep.when(Condition.booleanEquals('$.Payload.all_players_checked', false), getPlayerMatchesStep)
        forPlayerInListStep.when(Condition.booleanEquals('$.Payload.all_players_checked', true), finishPlayerLoop)

      getPlayerMatchesStep.next(checkForRiotBackoffMatchList)
        checkForRiotBackoffMatchList.when(Condition.numberEquals('$.Payload.match_result.status_code', 200), compareMatchesStep)
        checkForRiotBackoffMatchList.when(Condition.numberEquals('$.Payload.match_result.status_code', 429), waitForBackoffDurationMatchList)
        checkForRiotBackoffMatchList.when(Condition.numberGreaterThanEquals('$.Payload.match_result.status_code', 500), getPlayerMatchesStep)
        
      waitForBackoffDurationMatchList.next(getPlayerMatchesStep)
        
      compareMatchesStep.next(forMatchNotInCache)
        forMatchNotInCache.when(Condition.booleanEquals('$.Payload.all_matches_checked', true), writeMatchPlayerStep)
        forMatchNotInCache.when(Condition.booleanEquals('$.Payload.all_matches_checked', false), getMatchStep)
        
      getMatchStep.next(checkForRiotBackoffMatch)
        checkForRiotBackoffMatch.when(Condition.numberEquals('$.Payload.current_player.current_match.status_code', 200), writeMatchDataStep)
        checkForRiotBackoffMatch.when(Condition.numberEquals('$.Payload.current_player.current_match.status_code', 429), waitForBackoffDurationMatch)
        checkForRiotBackoffMatch.when(Condition.numberEquals('$.Payload.current_player.current_match.status_code', 404), failMatchStep)
        checkForRiotBackoffMatch.when(Condition.numberGreaterThanEquals('$.Payload.current_player.current_match.status_code', 500), getMatchStep)

      failMatchStep.next(forMatchNotInCache)

      waitForBackoffDurationMatch.next(getMatchStep)

      writeMatchDataStep.next(forMatchNotInCache)

      writeMatchPlayerStep.next(forPlayerInListStep)

    const matchProcessor = new StateMachine(this, 'LoR-State-Machine', {
      definition: stepDefinition,
      stateMachineName: "LoR-Match-Processor"
    })

    const scheduleStateMachine = new SfnStateMachine(matchProcessor)

    new Rule(this, 'LoR-Schedule-State-Machine', {
      schedule: Schedule.cron({ minute: '30', hour: '0'}),
      targets: [scheduleStateMachine],
      ruleName: "LoR-Match-Processor-Scheduler",
    })

  }
}
