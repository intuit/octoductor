import { ILogGroup } from "@aws-cdk/aws-logs";
import { Construct, Duration } from "@aws-cdk/core";
import { StateMachine,StateMachineType,LogLevel,IChainable } from '@aws-cdk/aws-stepfunctions';

export class OnboardingStateMachine extends StateMachine {

  constructor(scope: Construct, logGroup: ILogGroup, environment: string, definition: IChainable) {
    super(scope, 'OnboardingStateMachine', {
      definition: definition,
      logs: {
        destination: logGroup,
        includeExecutionData: true,
        level: LogLevel.ALL
      },
      stateMachineName: 'onboarding-workflow-' + environment,
      stateMachineType: StateMachineType.STANDARD,
      timeout: Duration.minutes(60)
    });
  }
}
