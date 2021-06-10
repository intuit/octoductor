import { IFunction } from '@aws-cdk/aws-lambda';

export interface ILambda extends IFunction {
    endpointName: string;
    httpMethod: string;
};
