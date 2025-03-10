# STage 1: Build the application

FROM eclipse-temurin:21-jdk AS builder                                                                                                            

WORKDIR /app                                                                                                                                      

# Copy only needed file first to cache dependencies

COPY ["src/adservice/build.gradle", "src/adservice/gradlew", "./"]                                                                                

COPY src/adservice/gradle gradle                                                                                                                  

# copy the rest of source code and build the app 

COPY src/adservice .    

RUN chmod +x gradlew && ./gradlew downloadRepos && \                                                                                              
     chmod +x gradlew && ./gradlew installDist                                                                                                     
  
# Stage 2: use minimal image to run the application

FROM eclipse-temurin:21-jre-alpine AS runtime                                                                                                     

WORKDIR /app                                                                                                                                      

# Copy only needed file of built application from the builder stage

COPY --from=builder /app/build/install/hipstershop /app                                                                                           

EXPOSE 9555                                                                                                                                       

ENTRYPOINT ["/app/bin/AdService"]