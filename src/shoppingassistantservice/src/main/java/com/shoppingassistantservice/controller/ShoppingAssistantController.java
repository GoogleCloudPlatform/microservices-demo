package com.shoppingassistantservice.controller;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.vertexai.VertexAiEmbeddingModel;
import dev.langchain4j.model.vertexai.VertexAiGeminiChatModel;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.spring.AiService;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.pgvector.PgVectorEmbeddingStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.PostConstruct;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;


@AiService
interface ShoppingChatAssistant {

    @UserMessage("You are a professional interior designer, give me a detailed decsription of the style of the room in this image: {{image}}")
    String getInteriorDesignResponse(String image);

    @UserMessage("You are an interior designer that works for Online Boutique. You are tasked with providing recommendations to a customer on what they should add to a given room from our catalog. This is the description of the room:  {{description_response}} Here are a list of products that are relevant to it: {{relevant_docs}} Specifically, this is what the customer has asked for, see if you can accommodate it: {{prompt}} Start by repeating a brief description of the room's design to the customer, then provide your recommendations. Do your best to pick the most relevant item out of the list of products provided, but if none of them seem relevant, then say that instead of inventing a new product. At the end of the response, add a list of the IDs of the relevant products in the following format for the top 3 results: [<first product ID>], [<second product ID>], [<third product ID>]")
    String getDesignRecommendations(String prompt, String description, String relevantDocs);
}

@RestController
class ShoppingAssistantController {

    Logger logger = LoggerFactory.getLogger(ShoppingAssistantController.class);

    @Autowired
    private static Environment environment;

    static final String PROJECT_ID = environment.getProperty("PROJECT_ID");
    static final String REGION = environment.getProperty("REGION");
    static final String ALLOYDB_DATABASE_NAME = environment.getProperty("ALLOYDB_DATABASE_NAME");
    static final String ALLOYDB_TABLE_NAME = environment.getProperty("ALLOYDB_TABLE_NAME");
    static final String ALLOYDB_CLUSTER_NAME = environment.getProperty("ALLOYDB_CLUSTER_NAME");
    static final String ALLOYDB_INSTANCE_NAME = environment.getProperty("ALLOYDB_INSTANCE_NAME");
    static final String ALLOYDB_SECRET_NAME = environment.getProperty("ALLOYDB_SECRET_NAME");

    private EmbeddingModel embeddingModel;
    private EmbeddingStore<TextSegment> pgVectorStore;


    @PostConstruct
    private void postConstruct() {
        embeddingModel = VertexAiEmbeddingModel.builder()
            .project(PROJECT_ID)
            .location(REGION)
            .endpoint(REGION+"-aiplatform.googleapis.com:443")
            .publisher("google")
            .modelName("textembedding-gecko@003")
            .build();

        pgVectorStore = PgVectorEmbeddingStore.builder()
            .host("localhost") //TODO: https://cloud.google.com/alloydb/docs/configure-private-service-connect#connect-with-dns
            .port(5432)
            .database(ALLOYDB_DATABASE_NAME)
            .user("user")
            .password(ALLOYDB_SECRET_NAME)
            .table(ALLOYDB_TABLE_NAME)
            .build();
    }

    @PostMapping("/")
    public String talkToGemini(@RequestBody Map<String, String> body) {
        String userSuppliedPrompt = body.get("prompt");
        logger.info("Beginning RAG call");

        VertexAiGeminiChatModel geminiFlash = VertexAiGeminiChatModel
            .builder()
            .modelName("gemini-1.5-flash")
            .build();

        ShoppingChatAssistant interiorDesignerAssistant = AiServices.builder(ShoppingChatAssistant.class)
            .chatLanguageModel(geminiFlash)
            .build();

        // Step 1 – Get a room description from Gemini-vision-pro
        String descriptionResponse = interiorDesignerAssistant.getInteriorDesignResponse(body.get("image"));
        logger.info("Description step:");
        logger.info(descriptionResponse);

        // Step 2 – Similarity search with the description & user prompt
        String vectorSearchPrompt = "This is the user's request:" + userSuppliedPrompt + " Find the most relevant items for that prompt, while matching style of the room described here: " + descriptionResponse;
        logger.info("Vector search:");
        logger.info(vectorSearchPrompt);

        //Retrieve the actual documents with a similarity search
        EmbeddingSearchResult<TextSegment> segmentEmbeddingSearchResult = pgVectorStore.search(EmbeddingSearchRequest.builder()
            .queryEmbedding(embeddingModel.embed(vectorSearchPrompt).content())
            .build());

        List<EmbeddingMatch<TextSegment>> matches = segmentEmbeddingSearchResult.matches();
        String matchingResults = matches.stream()
            .map(match -> {
                String matchText = match.embedded().text();
                logger.info("Retrieved " + matchText);
                return matchText;
            })
            .collect(Collectors.joining(" , "));

        // Step 3 – Tie it all together by augmenting our call to Gemini-pro
        String polishedRecommendation = interiorDesignerAssistant.getDesignRecommendations(userSuppliedPrompt, descriptionResponse, matchingResults);
        logger.info("Final design prompt: ");
        logger.info(polishedRecommendation);

        return polishedRecommendation;
    }

}
