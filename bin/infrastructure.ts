#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "@aws-cdk/core";
import { OctoductorStack } from "../lib/deployment/cdk-stack";

const app = new cdk.App();
new OctoductorStack(app, "OctoductorStack");
