import { join } from 'path';
import { Construct } from "@aws-cdk/core"
import { Runtime, LayerVersion, Code } from "@aws-cdk/aws-lambda"

export class CommonLayer extends LayerVersion {
    constructor(scope: Construct, id: string = 'OctoductorLayer') {
      super(scope, id, {
        compatibleRuntimes: [Runtime.PYTHON_3_7],
        code: Code.fromAsset(join(__dirname, '..', 'octoductor'), {
            bundling: {
              image: Runtime.PYTHON_3_7.bundlingDockerImage,
              command: [
                'bash', '-c', `
                pip install -r requirements.txt -t /asset-output/python/lib/python3.7/site-packages && 
                cp -au . /asset-output/python/lib/python3.7/site-packages &&
                rm -r /asset-output/python/lib/python3.7/site-packages/ui
                `,
              ],
            },
          }),
      });
    }
  }

export class CommonLayerSingleton {

    private static instance: CommonLayerSingleton;
    private layer: CommonLayer

    private constructor(scope: Construct) {
        this.layer = new CommonLayer(scope)
    }

    public static getInstance(scope: Construct): CommonLayerSingleton {
        if (!CommonLayerSingleton.instance) {
            CommonLayerSingleton.instance = new CommonLayerSingleton(scope);
        }
        return this.instance;
    }

    public getLayer(): CommonLayer {
        return this.layer
    }

}
