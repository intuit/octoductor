import { Construct, Stack } from '@aws-cdk/core';
import { CfnDBCluster, CfnDBSubnetGroup, AuroraPostgresEngineVersion, DatabaseClusterEngine, DatabaseSecret } from '@aws-cdk/aws-rds';
import { IVpc, SecurityGroup, SubnetType } from '@aws-cdk/aws-ec2';
import { Function } from '@aws-cdk/aws-lambda';
import { Secret } from '@aws-cdk/aws-secretsmanager';
import { SfnStateMachine, LambdaFunction } from '@aws-cdk/aws-events-targets';
import { Rule, IRuleTarget } from '@aws-cdk/aws-events';
import { Trail } from '@aws-cdk/aws-cloudtrail'
import { StateMachine } from '@aws-cdk/aws-stepfunctions'
import { IResolvable } from '@aws-cdk/core';

/**
 * Serverless construct not in place for Aurora yet, wrapping generic CFN.
 * https://github.com/aws/aws-cdk/issues/929
 * https://docs.aws.amazon.com/cdk/api/latest/docs/aws-rds-readme.html
 * https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-rds.CfnDBCluster.html
 * https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html
 */
export class ServerlessAurora extends Construct {
  public readonly MODE: string = 'serverless'
  public readonly VERSION: string = AuroraPostgresEngineVersion.VER_10_7.auroraPostgresFullVersion
  public readonly ENGINE: string = DatabaseClusterEngine.AURORA_POSTGRESQL.engineType

  private _cluster: CfnDBCluster;
  private _identifier: string;
  private _secret: Secret;
  private _defaultDB: string;

  constructor(scope: Construct,
    id: string,
    clusterName: string,
    readonly vpc: IVpc,
    pause: boolean | IResolvable = true,
    backupPeriod = 1,
    min = 2, max = 8, idleToPause = 300,
    defaultDB: string = "postgres") {

    super(scope, id);
    
    this._identifier = clusterName
    this._defaultDB = defaultDB
    this._secret = new DatabaseSecret(scope, id + 'Secret', {
      username: 'root',
    });

    const securityGroup = new SecurityGroup(this, id + 'SecurityGroup', {
      vpc,
      allowAllOutbound: true,
    });

    this._cluster = new CfnDBCluster(this, id + 'Cluster', {
      dbClusterIdentifier: this._identifier,
      engine: this.ENGINE,
      engineVersion: this.VERSION,
      engineMode: this.MODE,
      databaseName: this._defaultDB,
      masterUsername: this._secret.secretValueFromJson('username').toString(),
      masterUserPassword: this._secret.secretValueFromJson('password').toString(),
      vpcSecurityGroupIds: [securityGroup.securityGroupId],
      deletionProtection: false,
      enableHttpEndpoint: true,
      storageEncrypted: true,
      backupRetentionPeriod: backupPeriod,

      dbSubnetGroupName: new CfnDBSubnetGroup(this, id + 'SubnetGroup', {
        dbSubnetGroupDescription: 'AuroraSubnetGroup',
        subnetIds: vpc.selectSubnets({ subnetType: SubnetType.PRIVATE }).subnetIds,
      }).ref,

      scalingConfiguration: {
        autoPause: pause,
        minCapacity: min,
        maxCapacity: max,
        secondsUntilAutoPause: idleToPause
      },
    });
  }

  private addFilter(rule: Rule) {
    rule.addEventPattern({
      detail: {
        eventSource: ['rds.amazonaws.com'],
        eventName: ['CreateDBCluster'],
        responseElements: {
          dBClusterIdentifier: [this._identifier]
        }
      }
    });
  }

  public executeStateMachinOnClusterCreation(id: string, machine: StateMachine) {
    const rule = Trail.onEvent(this, id, {
      target: new SfnStateMachine(machine)
    });
    this.addFilter(rule);
    this._cluster.node.addDependency(machine)
    return rule;
  }

  public onClusterCreationEvent(id: string, fn: Function) {
    const rule = Trail.onEvent(this, id, {
      target: new LambdaFunction(fn)
    });
    this.addFilter(rule);
    this._cluster.node.addDependency(fn)
    return rule;
  }

  /**
   * Defines a CloudWatch event rule which triggers for cluster events. You can filter further
   * by applying additional event patterns to the rule.
   * 
   * Available events are documented here:
   * https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_Events.html
   * 
   * Note: Instance events are not available to serverless clusters.
   */
  public onClusterEvent(id: string, target: IRuleTarget) {
    const rule = new Rule(this, id);
    rule.addEventPattern({
      source: ['aws.rds'],
      resources: [this.clusterArn(this)],
      detail: {
        EventCategories: [
          'serverless',
        ],
      }
    });
    rule.addTarget(target);
    return rule;
  }

  /**
   * The cluster ARN.
   */
  public clusterArn(scope: Construct): string {
    return Stack.of(scope).formatArn({
      service: 'rds',
      resource: 'cluster',
      sep: ':',
      resourceName: this._identifier,
    });
  }

  public get secret(): Secret {
    return this._secret;
  }

  public get defaultDB(): string {
    return this._defaultDB;
  }
}
