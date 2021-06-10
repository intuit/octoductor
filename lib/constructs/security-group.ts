import { Construct } from '@aws-cdk/core';
import { SecurityGroup, Port, IVpc, ISecurityGroup} from "@aws-cdk/aws-ec2";

export class GlobalSecurityGroup extends SecurityGroup {
    constructor(scope: Construct, id: string, vpc: IVpc, allowAllOutbound: boolean = true, allowSGInternalTraffic: boolean = true) {
        super(scope, id, {
            vpc: vpc,
            allowAllOutbound: allowAllOutbound
        });

        if (allowSGInternalTraffic) {
            this.connections.allowInternally(Port.allTcp())
        };
    }
}
