import { Aws, Stack, CfnParameter, CfnCondition, Fn, IResolvable } from "@aws-cdk/core";
import { IVpc, Vpc } from "@aws-cdk/aws-ec2";
import { Certificate, ICertificate } from "@aws-cdk/aws-certificatemanager";
import { HostedZone, IHostedZone } from '@aws-cdk/aws-route53';
import { DomainNameOptions, SecurityPolicy } from "@aws-cdk/aws-apigateway";
import { ISecret, Secret } from "@aws-cdk/aws-secretsmanager";

export class ConfigurationParameters {
    private _scope: Stack;
    private _environment: CfnParameter;
    private _vpc: CfnParameter;
    private _vpcCidrBlock: CfnParameter;
    private _privateSubnetIds: CfnParameter;
    private _privateSubnetRouteTableIds: CfnParameter;
    private _hostedZoneId: CfnParameter;
    private _acmCertificateArn: CfnParameter;
    private _domainName: CfnParameter;
    private _githubSecretArn: CfnParameter;
    private _slackSecretArn: CfnParameter;
    private _slackSigningSecretArn: CfnParameter;
    private _isPR: CfnCondition;
    private _isProduction: CfnCondition;
    private _githubDomain: CfnParameter;
    private _githubAppId: CfnParameter;

    constructor(stack: Stack) {
        this._scope = stack;
        this._environment = new CfnParameter(stack, "EnvironmentName", {
            type: "String",
            default: "",
            description:
                "The name of the environment the stack is about to be deployed into",
        });
        this._vpc = new CfnParameter(stack, "VpcID", {
            type: "String",
            default: "",
            description: "The VPC within your account",
        });
        this._vpcCidrBlock = new CfnParameter(stack, "VpcCidrBlock", {
            type: "String",
            description: "VPC's CIDR range",
            default: ""
        });
        this._privateSubnetIds = new CfnParameter(stack, "PrivateSubnetIds", {
            type: "CommaDelimitedList",
            description: "List of private subnet IDs. Must be undefined or match the availability zones in length and order.",
            default: ""
        });
        this._privateSubnetRouteTableIds = new CfnParameter(stack, "PrivateSubnetRouteTableIds", {
            type: "CommaDelimitedList",
            description: "List of IDs of routing tables for the private subnets. Must be undefined or have a name for every private subnet group.",
            default: ""
        });
        this._hostedZoneId = new CfnParameter(stack, "HostedZoneId", {
            type: "String",
            description: "Can be found in Route53 under the hosted zone",
            default: ""
        });
        this._acmCertificateArn = new CfnParameter(stack, "AcmCertificateArn", {
            type: "String",
            description: "ARN of ACM certificate, can be found in AWS certificate manager (ACM)"
        });
        this._domainName = new CfnParameter(stack, "DomainName", {
            type: "String",
            description: "Static fully qualified domain name"
        });
        this._githubSecretArn = new CfnParameter(stack, "GithubSecretArn", {
            type: "String",
            description: "ARN for the GitHub application secrets (expecting 'secret' and Base64Encoded 'key')"
        });
        this._slackSecretArn = new CfnParameter(stack, "SlackSecretArn", {
            type: "String",
            description: "ARN for the Slack application secrets (expecting 'slackToken')"
        });
        this._slackSigningSecretArn = new CfnParameter(stack, "SlackSigningSecretArn", {
            type: "String",
            description: "ARN for the Slack signing secret - ingress traffic (expecting 'secret')"
        });

        this._isPR = new CfnCondition(this._scope, ConfigurationParameters.randomizedId(), {
            expression: Fn.conditionNot(
                Fn.conditionOr(
                    Fn.conditionEquals("dev", this.env),
                    Fn.conditionEquals("stg", this.env),
                    Fn.conditionEquals("prd", this.env)
                ))
        })

        this._isProduction = new CfnCondition(this._scope, ConfigurationParameters.randomizedId(), {
            expression:
                Fn.conditionOr(
                    Fn.conditionEquals("prd", this.env)
                )
        })

        this._githubDomain = new CfnParameter(stack, "GithubDomain", {
            type: "String",
            description: "URI for crawling Enterprise GitHub instance"
        });

        this._githubAppId = new CfnParameter(stack, "GithubApplicationId", {
            type: "String",
            description: "Application ID for crawling Enterprise GitHub instance"
        });
    };

    protected static randomizedId(): string {
        // Logical ID must adhere to the regular expression: /^[A-Za-z][A-Za-z0-9]{1,254}$/
        return 'r' + Math.random().toString(36).substring(7);
    }

    get vpcId(): string {
        const vpcId: string = `${this._vpc.valueAsString}`;
        return vpcId;
    }

    get env(): string {
        var env: string = `${this._environment.valueAsString}`;
        if (env == undefined) {
            env = 'dev'
        }
        return env;
    }

    get vpc(): IVpc {
        /**
         * Lookups need cdk cli.
         * https://github.com/aws/aws-cdk/issues/4096
         * https://github.com/aws/aws-cdk/issues/3600
         */
        return Vpc.fromVpcAttributes(this._scope, ConfigurationParameters.randomizedId(), {
            vpcId: this.vpcId,
            vpcCidrBlock: this._vpcCidrBlock.valueAsString,
            availabilityZones: Fn.getAzs(Aws.REGION),
            privateSubnetIds: this._privateSubnetIds.valueAsList,
            privateSubnetRouteTableIds: this._privateSubnetRouteTableIds.valueAsList
        });
    }

    get certificate(): ICertificate {
        return Certificate.fromCertificateArn(this._scope, ConfigurationParameters.randomizedId(), this._acmCertificateArn.valueAsString);
    }

    get hostedZone(): IHostedZone {
        return HostedZone.fromHostedZoneAttributes(this._scope, "ExistingPublicHostedZone", {
            hostedZoneId: this._hostedZoneId.valueAsString,
            zoneName: this._domainName.valueAsString
        });
    }

    public isPr(valueIfTrue: any, valueIfFalse: any): IResolvable {
        return Fn.conditionIf(
            this._isPR.logicalId,
            valueIfTrue,
            valueIfFalse)
    }

    public isProduction(valueIfTrue: any, valueIfFalse: any): IResolvable {
        return Fn.conditionIf(
            this._isProduction.logicalId,
            valueIfTrue,
            valueIfFalse)
    }

    get githubSecret(): ISecret {
        return Secret.fromSecretArn(this._scope,
            ConfigurationParameters.randomizedId(),
            this._githubSecretArn.valueAsString)
    }

    get slackSecret(): ISecret {
        return Secret.fromSecretArn(this._scope,
            ConfigurationParameters.randomizedId(),
            this._slackSecretArn.valueAsString)
    }

    get slackSigningSecret(): ISecret {
        return Secret.fromSecretArn(this._scope,
            ConfigurationParameters.randomizedId(),
            this._slackSigningSecretArn.valueAsString)
    }

    get domain(): DomainNameOptions {
        return {
            domainName: this.env + '.' + this._domainName.valueAsString,
            certificate: this.certificate,
            securityPolicy: SecurityPolicy.TLS_1_2
        }
    }

    get githubDomain(): string {
        return this._githubDomain.valueAsString
    }

    get githubAppId(): string {
        return this._githubAppId.valueAsString
    }

}
