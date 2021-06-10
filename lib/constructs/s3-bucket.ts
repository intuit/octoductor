import { Construct, RemovalPolicy} from '@aws-cdk/core';
import {BlockPublicAccess, Bucket, BucketEncryption} from '@aws-cdk/aws-s3';

export class S3Bucket extends Bucket {

  constructor(scope: Construct, id: string, bucketName: string) {
    super(scope, id, {
      versioned: false,
      bucketName: bucketName,
      encryption: BucketEncryption.KMS_MANAGED,
      publicReadAccess: false,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.DESTROY
    });
    
  }
    
}