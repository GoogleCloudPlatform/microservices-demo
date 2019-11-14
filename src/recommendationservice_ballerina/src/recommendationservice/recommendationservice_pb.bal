import ballerina/grpc;

public type RecommendationServiceBlockingClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function ListRecommendations(ListRecommendationsRequest req, grpc:Headers? headers = ()) returns ([ListRecommendationsResponse, grpc:Headers]|grpc:Error) {
        
        var payload = check self.grpcClient->blockingExecute("hipstershop.RecommendationService/ListRecommendations", req, headers);
        grpc:Headers resHeaders = new;
        anydata result = ();
        [result, resHeaders] = payload;
        var value = typedesc<ListRecommendationsResponse>.constructFrom(result);
        if (value is ListRecommendationsResponse) {
            return [value, resHeaders];
        } else {
            return grpc:prepareError(grpc:INTERNAL_ERROR, "Error while constructing the message", value);
        }
    }

};

public type RecommendationServiceClient client object {

    *grpc:AbstractClientEndpoint;

    private grpc:Client grpcClient;

    public function __init(string url, grpc:ClientConfiguration? config = ()) {
        // initialize client endpoint.
        grpc:Client c = new(url, config);
        grpc:Error? result = c.initStub(self, "non-blocking", ROOT_DESCRIPTOR, getDescriptorMap());
        if (result is grpc:Error) {
            error err = result;
            panic err;
        } else {
            self.grpcClient = c;
        }
    }

    public remote function ListRecommendations(ListRecommendationsRequest req, service msgListener, grpc:Headers? headers = ()) returns (grpc:Error?) {
        
        return self.grpcClient->nonBlockingExecute("hipstershop.RecommendationService/ListRecommendations", req, msgListener, headers);
    }

};

public type ListRecommendationsRequest record {|
    string user_id;
    string[] product_ids;
    
|};


public type ListRecommendationsResponse record {|
    string[] product_ids;
    
|};



const string ROOT_DESCRIPTOR = "0A1B7265636F6D6D656E646174696F6E736572766963652E70726F746F120B6869707374657273686F7022560A1A4C6973745265636F6D6D656E646174696F6E735265717565737412170A07757365725F69641801200128095206757365724964121F0A0B70726F647563745F696473180220032809520A70726F64756374496473223E0A1B4C6973745265636F6D6D656E646174696F6E73526573706F6E7365121F0A0B70726F647563745F696473180120032809520A70726F647563744964733283010A155265636F6D6D656E646174696F6E53657276696365126A0A134C6973745265636F6D6D656E646174696F6E7312272E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526571756573741A282E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526573706F6E73652200620670726F746F33";
function getDescriptorMap() returns map<string> {
    return {
        "recommendationservice.proto":"0A1B7265636F6D6D656E646174696F6E736572766963652E70726F746F120B6869707374657273686F7022560A1A4C6973745265636F6D6D656E646174696F6E735265717565737412170A07757365725F69641801200128095206757365724964121F0A0B70726F647563745F696473180220032809520A70726F64756374496473223E0A1B4C6973745265636F6D6D656E646174696F6E73526573706F6E7365121F0A0B70726F647563745F696473180120032809520A70726F647563744964733283010A155265636F6D6D656E646174696F6E53657276696365126A0A134C6973745265636F6D6D656E646174696F6E7312272E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526571756573741A282E6869707374657273686F702E4C6973745265636F6D6D656E646174696F6E73526573706F6E73652200620670726F746F33"
        
    };
}

