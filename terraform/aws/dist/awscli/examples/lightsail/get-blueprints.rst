**To get the blueprints for new instances**

The following ``get-blueprints`` example displays details about all of the available blueprints that can be used to create new instances in Amazon Lightsail. ::

    aws lightsail get-blueprints

Output::

    {
        "blueprints": [
            {
                "blueprintId": "wordpress",
                "name": "WordPress",
                "group": "wordpress",
                "type": "app",
                "description": "Bitnami, the leaders in application packaging, and Automattic, the experts behind WordPress, have teamed up to offer this official WordPress image. This image is a pre-configured, ready-to-run image for running WordPress on Amazon Lightsail. WordPress is the world's most popular content management platform. Whether it's for an enterprise or small business website, or a personal or corporate blog, content authors can easily create content using its new Gutenberg editor, and developers can extend the base platform with additional features. Popular plugins like Jetpack, Akismet, All in One SEO Pack, WP Mail, Google Analytics for WordPress, and Amazon Polly are all pre-installed in this image. Let's Encrypt SSL certificates are supported through an auto-configuration script.",
                "isActive": true,
                "minPower": 0,
                "version": "5.2.2-3",
                "versionCode": "1",
                "productUrl": "https://aws.amazon.com/marketplace/pp/B00NN8Y43U",
                "licenseUrl": "https://d7umqicpi7263.cloudfront.net/eula/product/7d426cb7-9522-4dd7-a56b-55dd8cc1c8d0/588fd495-6492-4610-b3e8-d15ce864454c.txt",
                "platform": "LINUX_UNIX"
            },
            {
                "blueprintId": "lamp_7_1_28",
                "name": "LAMP (PHP 7)",
                "group": "lamp_7",
                "type": "app",
                "description": "LAMP with PHP 7.x certified by Bitnami greatly simplifies the development and deployment of PHP applications. It includes the latest versions of PHP 7.x, Apache and MySQL together with phpMyAdmin and popular PHP frameworks Zend, Symfony, CodeIgniter, CakePHP, Smarty, and Laravel. Other pre-configured components and PHP modules include FastCGI, ModSecurity, SQLite, Varnish, ImageMagick, xDebug, Xcache, OpenLDAP, Memcache, OAuth, PEAR, PECL, APC, GD and cURL. It is secure by default and supports multiple applications, each with its own virtual host and project directory. Let's Encrypt SSL certificates are supported through an auto-configuration script.",
                "isActive": true,
                "minPower": 0,
                "version": "7.1.28",
                "versionCode": "1",
                "productUrl": "https://aws.amazon.com/marketplace/pp/B072JNJZ5C",
                "licenseUrl": "https://d7umqicpi7263.cloudfront.net/eula/product/cb6afd05-a3b2-4916-a3e6-bccd414f5f21/12ab56cc-6a8c-4977-9611-dcd770824aad.txt",
                "platform": "LINUX_UNIX"
            },
            {
                "blueprintId": "nodejs",
                "name": "Node.js",
                "group": "node",
                "type": "app",
                "description": "Node.js certified by Bitnami is a pre-configured, ready to run image for Node.js on Amazon EC2. It includes the latest version of Node.js, Apache, Python and Redis. The image supports multiple Node.js applications, each with its own virtual host and project directory. It is configured for production use and is secure by default, as all ports except HTTP, HTTPS and SSH ports are closed. Let's Encrypt SSL certificates are supported through an auto-configuration script. Developers benefit from instant access to a secure, update and consistent Node.js environment without having to manually install and configure multiple components and libraries.",
                "isActive": true,
                "minPower": 0,
                "version": "12.7.0",
                "versionCode": "1",
                "productUrl": "https://aws.amazon.com/marketplace/pp/B00NNZUAKO",
                "licenseUrl": "https://d7umqicpi7263.cloudfront.net/eula/product/033793fe-951d-47d0-aa94-5fbd0afb3582/25f8fa66-c868-4d80-adf8-4a2b602064ae.txt",
                "platform": "LINUX_UNIX"
            },
            ...
            }
        ]
    }
