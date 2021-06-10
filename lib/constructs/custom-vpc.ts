import { Construct, RemovalPolicy } from "@aws-cdk/core";
import { DefaultInstanceTenancy, FlowLogDestination, NatProvider, SubnetType, Vpc, IVpc} from "@aws-cdk/aws-ec2";
import { BlockPublicAccess, Bucket, BucketEncryption } from "@aws-cdk/aws-s3";

export class CustomVpc extends Construct {
    public vpc: IVpc;
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const flow_logs_bucket = new Bucket(this, id + 'FlowLogs', {
            versioned: false,
            bucketName: id.toLowerCase() + '-flow-logs',
            encryption: BucketEncryption.KMS_MANAGED,
            publicReadAccess: false,
            blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
            removalPolicy: RemovalPolicy.DESTROY
        });

        const vpc = new Vpc(this, id + "Vpc", {
            defaultInstanceTenancy: DefaultInstanceTenancy.DEFAULT,
            enableDnsHostnames: true,
            enableDnsSupport: true,
            flowLogs: { flowLog1: { destination: FlowLogDestination.toS3(flow_logs_bucket) } },
            maxAzs: 4,
            natGatewayProvider: NatProvider.gateway(),
            natGatewaySubnets: { subnetType: SubnetType.PUBLIC, onePerAz: true },
            vpnGateway: false,
            subnetConfiguration: [
                {
                    cidrMask: 23,
                    name: 'Ingress',
                    subnetType: SubnetType.ISOLATED,
                    reserved: false
                },
                {
                    cidrMask: 27,
                    name: 'Egress',
                    subnetType: SubnetType.PUBLIC,
                    reserved: false
                },
                {
                    cidrMask: 25,
                    name: 'Private',
                    subnetType: SubnetType.PRIVATE,
                    reserved: false
                }
            ]
        });

        this.vpc = vpc

    }
}
