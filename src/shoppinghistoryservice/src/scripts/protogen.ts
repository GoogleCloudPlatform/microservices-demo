import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

const protoFile = 'src/proto/shopping_history.proto'; // Adjust path as needed
const outputDir = 'src/proto';

const command = `
  npx protoc \
    --plugin=protoc-gen-ts_proto=./node_modules/.bin/protoc-gen-ts_proto \
    --ts_proto_out=${outputDir} \
    --ts_proto_opt=esModuleInterop=true,forceLong=string,useGrpcJs=true,addGrpcMetadata=true \
    -Isrc/proto \
    -Inode_modules/ts-proto/include \
    ${protoFile}
`;

async function generate() {
  try {
    console.log('Generating TypeScript types from .proto...');
    const { stdout, stderr } = await execPromise(command);

    if (stderr) {
      console.error('Protobuf generation error:', stderr);
      return;
    }

    console.log('Protobuf generation successful!');
    console.log(stdout);
  } catch (error) {
    console.error('Failed to run protoc:', error);
  }
}

generate();
