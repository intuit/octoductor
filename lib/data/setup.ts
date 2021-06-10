import { join } from 'path';
import { Construct, Duration } from '@aws-cdk/core';
import { PythonFunction } from '@aws-cdk/aws-lambda-python'
import { IVpc, SubnetType } from "@aws-cdk/aws-ec2";
import { StateMachine, TaskStateBase } from '@aws-cdk/aws-stepfunctions';
import { LambdaInvoke } from '@aws-cdk/aws-stepfunctions-tasks';
import { ClusterConnection} from '../cluster-connection'
import * as sm from '@aws-cdk/aws-secretsmanager';
import * as iam from '@aws-cdk/aws-iam';
import * as rds from '@aws-cdk/aws-rds';

class SetupFunction extends PythonFunction {
    constructor(scope: Construct, id: string, vpc: IVpc, handler: string, connection: ClusterConnection, read: sm.Secret, write: sm.Secret) {
        super(scope, id, {
            entry: join(__dirname, '..', '..', 'octoductor', 'data', 'setup'),
            handler: handler,
            vpc: vpc,
            vpcSubnets: { subnetType: SubnetType.PRIVATE },
            environment: {
                DB_CLUSTER_ARN: connection.clusterArn,
                DB_ADMIN_CREDENTIALS_ARN: connection.credentials.secretArn,
                DB_NAME: connection.database,
                DB_READ_CREDENTIALS_ARN: read.secretArn,
                DB_WRITE_CREDENTIALS_ARN: write.secretArn
            },
            timeout: Duration.minutes(1)
        })
        connection.credentials.grantRead(this)
        read.grantRead(this)
        write.grantRead(this)
        this.role!.addToPrincipalPolicy(new iam.PolicyStatement({
            actions: ['rds-data:*'],
            resources: [connection.clusterArn]
        }))
    }
}

class Steps {
    readonly read: sm.Secret;
    readonly write: sm.Secret;
    readonly connection: ClusterConnection;
    readonly scope: Construct
    readonly vpc: IVpc;

    constructor(scope: Construct, vpc: IVpc, connection: ClusterConnection) {
        this.scope = scope
        this.vpc = vpc
        this.connection = connection
        this.read = new rds.DatabaseSecret(scope, 'ReadOnlySecret', {
            username: 'readonly',
        });
        this.write = new rds.DatabaseSecret(scope, 'ReadWriteSecret', {
            username: 'readwrite',
        });
    }

    public get users(): TaskStateBase {
        return this.invoke('Users', 'users');
    }

    public get tables(): TaskStateBase {
        return this.invoke('Tables', 'tables');
    }

    public get access(): TaskStateBase {
        return this.invoke('Access', 'access');
    }

    public get wait(): TaskStateBase {
        return this.invoke('Wait', 'await_connection');
    }

    private invoke(id: string, handler: string): TaskStateBase {
        return new LambdaInvoke(this.scope, id + ' Invocation', {
            lambdaFunction: new SetupFunction(this.scope, id, this.vpc, handler, this.connection, this.read, this.write)
        });
    }
}

export class Setup extends StateMachine {
    readonly read: sm.Secret;
    readonly write: sm.Secret;

    constructor(scope: Construct, id: string, vpc: IVpc, secret: sm.Secret, db_arn: string, database: string) {
        let connection = new ClusterConnection(db_arn, secret, database)
        let steps = new Steps(scope, vpc, connection)
        super(scope, id, {
            definition:
            steps.wait
                .next(steps.users)
                .next(steps.tables)
                .next(steps.access),
            timeout: Duration.minutes(5)
        });

        this.read = steps.read
        this.write = steps.write
    }
}
