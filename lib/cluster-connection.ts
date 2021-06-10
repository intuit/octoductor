import { Secret } from '@aws-cdk/aws-secretsmanager';

export class ClusterConnection {
    constructor(readonly clusterArn: string, readonly credentials: Secret, readonly database: string) { }
}
