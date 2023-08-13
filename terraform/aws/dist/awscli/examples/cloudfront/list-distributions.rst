**To list CloudFront distributions**

The following example gets a list of the CloudFront distributions in your AWS
account::

    aws cloudfront list-distributions

Output::

    {
        "DistributionList": {
            "Items": [
                {
                    "Id": "EMLARXS9EXAMPLE",
                    "ARN": "arn:aws:cloudfront::123456789012:distribution/EMLARXS9EXAMPLE",
                    "Status": "InProgress",
                    "LastModifiedTime": "2019-11-22T00:55:15.705Z",
                    "InProgressInvalidationBatches": 0,
                    "DomainName": "d111111abcdef8.cloudfront.net",
                    "ActiveTrustedSigners": {
                        "Enabled": false,
                        "Quantity": 0
                    },
                    "DistributionConfig": {
                        "CallerReference": "cli-example",
                        "Aliases": {
                            "Quantity": 0
                        },
                        "DefaultRootObject": "index.html",
                        "Origins": {
                            "Quantity": 1,
                            "Items": [
                                {
                                    "Id": "awsexamplebucket.s3.amazonaws.com-cli-example",
                                    "DomainName": "awsexamplebucket.s3.amazonaws.com",
                                    "OriginPath": "",
                                    "CustomHeaders": {
                                        "Quantity": 0
                                    },
                                    "S3OriginConfig": {
                                        "OriginAccessIdentity": ""
                                    }
                                }
                            ]
                        },
                        "OriginGroups": {
                            "Quantity": 0
                        },
                        "DefaultCacheBehavior": {
                            "TargetOriginId": "awsexamplebucket.s3.amazonaws.com-cli-example",
                            "ForwardedValues": {
                                "QueryString": false,
                                "Cookies": {
                                    "Forward": "none"
                                },
                                "Headers": {
                                    "Quantity": 0
                                },
                                "QueryStringCacheKeys": {
                                    "Quantity": 0
                                }
                            },
                            "TrustedSigners": {
                                "Enabled": false,
                                "Quantity": 0
                            },
                            "ViewerProtocolPolicy": "allow-all",
                            "MinTTL": 0,
                            "AllowedMethods": {
                                "Quantity": 2,
                                "Items": [
                                    "HEAD",
                                    "GET"
                                ],
                                "CachedMethods": {
                                    "Quantity": 2,
                                    "Items": [
                                        "HEAD",
                                        "GET"
                                    ]
                                }
                            },
                            "SmoothStreaming": false,
                            "DefaultTTL": 86400,
                            "MaxTTL": 31536000,
                            "Compress": false,
                            "LambdaFunctionAssociations": {
                                "Quantity": 0
                            },
                            "FieldLevelEncryptionId": ""
                        },
                        "CacheBehaviors": {
                            "Quantity": 0
                        },
                        "CustomErrorResponses": {
                            "Quantity": 0
                        },
                        "Comment": "",
                        "Logging": {
                            "Enabled": false,
                            "IncludeCookies": false,
                            "Bucket": "",
                            "Prefix": ""
                        },
                        "PriceClass": "PriceClass_All",
                        "Enabled": true,
                        "ViewerCertificate": {
                            "CloudFrontDefaultCertificate": true,
                            "MinimumProtocolVersion": "TLSv1",
                            "CertificateSource": "cloudfront"
                        },
                        "Restrictions": {
                            "GeoRestriction": {
                                "RestrictionType": "none",
                                "Quantity": 0
                            }
                        },
                        "WebACLId": "",
                        "HttpVersion": "http2",
                        "IsIPV6Enabled": true
                    }
                },
                {
                    "Id": "EDFDVBD6EXAMPLE",
                    "ARN": "arn:aws:cloudfront::123456789012:distribution/EDFDVBD6EXAMPLE",
                    "Status": "InProgress",
                    "LastModifiedTime": "2019-12-04T23:35:41.433Z",
                    "InProgressInvalidationBatches": 0,
                    "DomainName": "d930174dauwrn8.cloudfront.net",
                    "ActiveTrustedSigners": {
                        "Enabled": false,
                        "Quantity": 0
                    },
                    "DistributionConfig": {
                        "CallerReference": "cli-example",
                        "Aliases": {
                            "Quantity": 0
                        },
                        "DefaultRootObject": "index.html",
                        "Origins": {
                            "Quantity": 1,
                            "Items": [
                                {
                                    "Id": "awsexamplebucket1.s3.amazonaws.com-cli-example",
                                    "DomainName": "awsexamplebucket1.s3.amazonaws.com",
                                    "OriginPath": "",
                                    "CustomHeaders": {
                                        "Quantity": 0
                                    },
                                    "S3OriginConfig": {
                                        "OriginAccessIdentity": ""
                                    }
                                }
                            ]
                        },
                        "OriginGroups": {
                            "Quantity": 0
                        },
                        "DefaultCacheBehavior": {
                            "TargetOriginId": "awsexamplebucket1.s3.amazonaws.com-cli-example",
                            "ForwardedValues": {
                                "QueryString": false,
                                "Cookies": {
                                    "Forward": "none"
                                },
                                "Headers": {
                                    "Quantity": 0
                                },
                                "QueryStringCacheKeys": {
                                    "Quantity": 0
                                }
                            },
                            "TrustedSigners": {
                                "Enabled": false,
                                "Quantity": 0
                            },
                            "ViewerProtocolPolicy": "allow-all",
                            "MinTTL": 0,
                            "AllowedMethods": {
                                "Quantity": 2,
                                "Items": [
                                    "HEAD",
                                    "GET"
                                ],
                                "CachedMethods": {
                                    "Quantity": 2,
                                    "Items": [
                                        "HEAD",
                                        "GET"
                                    ]
                                }
                            },
                            "SmoothStreaming": false,
                            "DefaultTTL": 86400,
                            "MaxTTL": 31536000,
                            "Compress": false,
                            "LambdaFunctionAssociations": {
                                "Quantity": 0
                            },
                            "FieldLevelEncryptionId": ""
                        },
                        "CacheBehaviors": {
                            "Quantity": 0
                        },
                        "CustomErrorResponses": {
                            "Quantity": 0
                        },
                        "Comment": "",
                        "Logging": {
                            "Enabled": false,
                            "IncludeCookies": false,
                            "Bucket": "",
                            "Prefix": ""
                        },
                        "PriceClass": "PriceClass_All",
                        "Enabled": true,
                        "ViewerCertificate": {
                            "CloudFrontDefaultCertificate": true,
                            "MinimumProtocolVersion": "TLSv1",
                            "CertificateSource": "cloudfront"
                        },
                        "Restrictions": {
                            "GeoRestriction": {
                                "RestrictionType": "none",
                                "Quantity": 0
                            }
                        },
                        "WebACLId": "",
                        "HttpVersion": "http2",
                        "IsIPV6Enabled": true
                    }
                },
                {
                    "Id": "E1X5IZQEXAMPLE",
                    "ARN": "arn:aws:cloudfront::123456789012:distribution/E1X5IZQEXAMPLE",
                    "Status": "Deployed",
                    "LastModifiedTime": "2019-11-06T21:31:48.864Z",
                    "DomainName": "d2e04y12345678.cloudfront.net",
                    "Aliases": {
                        "Quantity": 0
                    },
                    "Origins": {
                        "Quantity": 1,
                        "Items": [
                            {
                                "Id": "awsexamplebucket2",
                                "DomainName": "awsexamplebucket2.s3.us-west-2.amazonaws.com",
                                "OriginPath": "",
                                "CustomHeaders": {
                                    "Quantity": 0
                                },
                                "S3OriginConfig": {
                                    "OriginAccessIdentity": ""
                                }
                            }
                        ]
                    },
                    "OriginGroups": {
                        "Quantity": 0
                    },
                    "DefaultCacheBehavior": {
                        "TargetOriginId": "awsexamplebucket2",
                        "ForwardedValues": {
                            "QueryString": false,
                            "Cookies": {
                                "Forward": "none"
                            },
                            "Headers": {
                                "Quantity": 0
                            },
                            "QueryStringCacheKeys": {
                                "Quantity": 0
                            }
                        },
                        "TrustedSigners": {
                            "Enabled": false,
                            "Quantity": 0
                        },
                        "ViewerProtocolPolicy": "allow-all",
                        "MinTTL": 0,
                        "AllowedMethods": {
                            "Quantity": 2,
                            "Items": [
                                "HEAD",
                                "GET"
                            ],
                            "CachedMethods": {
                                "Quantity": 2,
                                "Items": [
                                    "HEAD",
                                    "GET"
                                ]
                            }
                        },
                        "SmoothStreaming": false,
                        "DefaultTTL": 86400,
                        "MaxTTL": 31536000,
                        "Compress": false,
                        "LambdaFunctionAssociations": {
                            "Quantity": 0
                        },
                        "FieldLevelEncryptionId": ""
                    },
                    "CacheBehaviors": {
                        "Quantity": 0
                    },
                    "CustomErrorResponses": {
                        "Quantity": 0
                    },
                    "Comment": "",
                    "PriceClass": "PriceClass_All",
                    "Enabled": true,
                    "ViewerCertificate": {
                        "CloudFrontDefaultCertificate": true,
                        "MinimumProtocolVersion": "TLSv1",
                        "CertificateSource": "cloudfront"
                    },
                    "Restrictions": {
                        "GeoRestriction": {
                            "RestrictionType": "none",
                            "Quantity": 0
                        }
                    },
                    "WebACLId": "",
                    "HttpVersion": "HTTP1_1",
                    "IsIPV6Enabled": true
                }
            ]
        }
    }
