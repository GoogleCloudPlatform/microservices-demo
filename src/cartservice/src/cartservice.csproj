<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net7.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Grpc.AspNetCore" Version="2.53.0" />
    <PackageReference Include="Grpc.HealthCheck" Version="2.53.0" />
    <PackageReference Include="Microsoft.Extensions.Caching.StackExchangeRedis" Version="7.0.5" />
    <!-- Add explicit direct dependency required for ipv6, see https://github.com/dotnet/aspnetcore/issues/45424 -->
    <PackageReference Include="StackExchange.Redis" Version="2.6.111" />
    <PackageReference Include="Google.Cloud.Spanner.Data" Version="4.5.0" />
    <PackageReference Include="Npgsql" Version="7.0.4" />
    <PackageReference Include="Google.Cloud.SecretManager.V1" Version="2.1.0" />
  </ItemGroup>

  <ItemGroup>
    <Protobuf Include="protos\Cart.proto" GrpcServices="Both" />
  </ItemGroup>
</Project>
