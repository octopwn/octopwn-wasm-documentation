# OctoPwn Security Documentation

Welcome to OctoPwn's security documentation! We prioritize safeguarding your interactions and data and are dedicated to maintaining a transparent and robust security posture.

## Hosting Methods

### Data In Transit and Storage

At OctoPwn, we employ HTTPS to secure data in transit, relying on SSL policies meticulously managed by Google Cloud Platform (GCP). Our data is stored in a public Google bucket, granting read access to everyone given that our framework is open.

### Responsibility for Unofficial Hosting

When it comes to unofficial hosting, please be aware that security assurance lies solely with the users. We cannot extend our security guarantees to platforms beyond our management.

## Plugin System

### Credential Protection Mechanism

Our plugin system features a credential protection mechanism, an additional protective layer over the SSL/TLS, designed to enhance backend security. This layer ensures stability and protection for our backend systems, and for the sake of maintaining its efficacy, further details are proprietary.

### Offline Version

In offline variants, users are tasked with managing private keys/certificates issued by our backend system. Unfortunately, we cannot assure security in these scenarios.

## Browser Security

### Data Representation Layer

At OctoPwn, data rendering employs a dual-layered approach to prevent Cross-Site Scripting (XSS):
1. **Terminal Data**: Using `xterm.js`, all input data is rendered in an HTML5 canvas to mitigate XSS vulnerabilities.
2. **Datatables**: Data rendered in datatables is purified cell-by-cell using the DOMPurify package to ensure a sanitized output.

## User Management

### Authentication and Access Control

Our licensing system facilitates user authentication and access control, exclusive to plugins. Here, three distinct user authentication endpoints are employed:
1. **Registration**: Managed by Fusionauth.
2. **Certificate-based authentication**: Users automatically receive an RSA2048 bit certificate and private key, with the certificate signed by OctoPwn and verified via our `/verify` endpoint.
3. **Username and password authentication**: The licensing system releases user’s certificates and private keys encrypted by a transient AES256 key after user authentication.

The details regarding cryptographic practices and data flow in these authentication modes are elaborately designed to maintain secure user interactions.

## Incident Response

Our team is in the process of developing a structured incident response plan, which will be aimed at efficiently managing and mitigating any security incidents, ensuring transparent communication with affected parties, and implementing corrective actions.

## Data Handling

### Session File Management

OctoPwn manages only the session file, stored securely in the browser's local storage. The entire session file employs a mandatory encryption layer that relies on a secret password which is either set by the user (recommended) or uses the user's internal user ID. Users are advised to securely manage and delete session data when operating on third-party machines.

## Security Measures

### Updates and Patches

Updates and patches are delivered via our CDN, which users will automatically download upon refreshing the OctoPwn page, maintaining the same security guarantees as all other backend-served files.

### Logging and Monitoring

Our backend systems are overseen by logging and monitoring mechanisms provided by Google Cloud, ensuring performance and security metrics are consistently scrutinized.

## General Remarks

We strive to deliver as much information as possible regarding the security of our systems. While our commitment is towards maintaining transparency and safeguarding user interactions and data, please note that certain backend system details remain undisclosed to protect our intellectual property.

## Continuous Improvement

Our security posture is under perpetual refinement. We continuously monitor, review, and enhance our security policies and practices to ensure alignment with emerging threats and technological advancements.

## External Audits and Certifications

We are exploring external security audits and certifications and are in the phase of aligning our practices with recognized cybersecurity frameworks to further affirm our commitment to robust cybersecurity practices.

## Data Protection and Privacy

Our practices are tailored to protect your data and uphold privacy, aligning with applicable data protection regulations. Details on our adherence to these regulatory environments will be shared in our upcoming data protection documentation.

## Conclusion

Thank you for engaging with our security documentation. Your trust and security are paramount to us at OctoPwn, and we remain dedicated to safeguarding your digital interactions and data. For further inquiries, please [contact us](mailto:[email protected]).

