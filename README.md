# AI Image Label Generator

A fully serverless image analysis application built on AWS. Everyday objects aren't always easy to identify — this tool lets users upload an image and instantly get a list of detected labels, confidence scores, and scene context powered by Amazon Rekognition.

---

## Live Demo

https://staging.d3w1w0m6iehn9k.amplifyapp.com/

---

## Architecture

![Architecture Diagram](architecture.png)

---

## Overview

This project implements a fully serverless image recognition system without requiring any server management.

## AWS Services Used

- AWS Amplify – Frontend hosting with automatic CI/CD on push
- Amazon API Gateway – Public-facing REST API endpoint
- AWS Lambda – Backend logic and Rekognition integration (Python)
- Amazon S3 – Image storage and presigned URL generation
- Amazon Rekognition – AI-powered label and scene detection

---

## Request Flow

When a user uploads an image:

1. The frontend requests a presigned upload URL from API Gateway
2. API Gateway triggers a Lambda function
3. Lambda generates a temporary presigned URL for the target S3 bucket
4. The browser uploads the image directly to S3, bypassing Lambda entirely
5. The frontend sends the uploaded S3 object key to Lambda
6. Lambda calls Amazon Rekognition with the object key
7. Rekognition returns detected labels and confidence scores
8. The frontend displays the results to the user

---

## Design Decisions

- Direct-to-S3 uploads via presigned URLs — Lambda has a 6MB request payload limit, making it unsuitable for passing image files directly. Presigned URLs allow the browser to upload straight to S3 regardless of file size, keeping Lambda out of the upload path entirely
- Amazon Rekognition — chosen as a managed AI service to explore computer vision without building or training a model. As a first integration with an AI service, it provided a clear entry point into machine learning on AWS
- AWS Amplify over S3 static hosting — Amplify provides automatic CI/CD, meaning every push to GitHub triggers a redeployment without any manual steps. Simpler and faster for an active project
- API Gateway — acts as a secure, managed public endpoint with built-in request throttling to prevent abuse

---

## Key Learnings

- Presigned URLs are more powerful than they first appear — rather than routing file uploads through your backend, S3 presigned URLs let the browser upload directly to storage. This removes payload size constraints and keeps Lambda focused on logic rather than acting as a file proxy
- Amazon Rekognition requires no ML knowledge to integrate — as a first experience with an AI service, the integration was surprisingly approachable. You provide an S3 object key, Rekognition handles the analysis entirely, and the response is a clean JSON list of labels and confidence scores ready to display
- AWS services are designed to talk to each other — rather than downloading an image from S3 and re-uploading it to Rekognition, Lambda can simply pass the bucket name and object key. The services handle the rest internally, which simplifies the code significantly
- CORS issues are common at the API Gateway and S3 boundary — direct browser-to-S3 uploads and API Gateway calls both require explicit CORS configuration. Regional endpoint mismatches on presigned URLs were a particular source of errors during development

---

## What I Would Do Differently

- Swap or supplement Rekognition with a more capable model for fine-grained label detection
- Add upload controls and S3 lifecycle policies to prevent storage abuse
- Give users more control over response filtering, such as setting a minimum confidence threshold

---

## Contact

Open to internship and graduate opportunities in software engineering and cloud computing.

- Email: nevenspooner03@gmail.com
- LinkedIn: https://www.linkedin.com/in/neven-spooner/
