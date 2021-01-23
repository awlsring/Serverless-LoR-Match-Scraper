import {Stack, StackProps, Construct} from 'monocdk';
import {Bucket} from 'monocdk/aws-s3'
import {BucketDeployment, Source} from 'monocdk/aws-s3-deployment'
import {Function, Runtime, Code, Tracing, LayerVersion} from 'monocdk/aws-lambda'

export class ResourcesStack extends Stack {

  public buckets: Map<string, string> = new Map;
  public lambdaLayers: Map<string, LayerVersion> = new Map;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Lambda Layers Layer
    const requestsLayer = new LayerVersion(this, "Requests-Layer", {
      code: Code.fromAsset('lib/handlers/lib/requests/requests.zip'),
      compatibleRuntimes: [ Runtime.PYTHON_3_8 ] ,
      description: "Lambda Layer for Requests",
      layerVersionName: "LoR-Requests"
    })

    const lorDeckCodesLayer = new LayerVersion(this, "LoR-Deck-Codes-Layer", {
      code: Code.fromAsset('lib/handlers/lib/lor-deckcodes/lor-deckcodes.zip'),
      compatibleRuntimes: [ Runtime.PYTHON_3_8 ] ,
      description: "Lambda Layer for LoR Deck Codes",
      layerVersionName: "LoR-Deck-Codes"
    })

    const lorUtilitiesLayer = new LayerVersion(this, "LoR-Utilities-Layer", {
      code: Code.fromAsset('lib/handlers/lib/lor-utilities/lor-utilities.zip'),
      compatibleRuntimes: [ Runtime.PYTHON_3_8 ] ,
      description: "Lambda Layer for LoR Utility Functions",
      layerVersionName: "LoR-Utilities"
    })

    this.lambdaLayers.set("requests", requestsLayer)
    this.lambdaLayers.set("lor-deckcodes", lorDeckCodesLayer)
    this.lambdaLayers.set("lor-utilities", lorUtilitiesLayer)

    // Bucket
    const frontEndBucket = new Bucket(this, 'LoR-React-Bucket', {
        bucketName: "lor-match-tracker-react-bucket",
        publicReadAccess: true,
        websiteIndexDocument: "index.html",
        websiteErrorDocument: "index.html",
    })

    const deployment = new BucketDeployment(this, "deployStaticWebsite", {
      sources: [Source.asset("build")],
      destinationBucket: frontEndBucket
   });

  }
}