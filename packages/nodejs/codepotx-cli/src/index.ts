#!/usr/bin/env node

import { runCli } from './main';

const exitCode = await runCli();
process.exitCode = exitCode;
