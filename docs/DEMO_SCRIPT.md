# Moviq 2-Minute Technical Product Demo Script & Narration

> **Target Duration**: 2 Minutes 15 Seconds  
> **Audience**: Engineering Managers, Technical Recruiter, Open Source Community  

---

## Timeline & Narration Script

### [0:00 - 0:20] Introduction & Problem Statement
- **Visual**: Screen opens on Moviq Create Studio interface with dark glassmorphism styling.
- **Narration**: *"Welcome to Moviq, an open-source AI video generation platform built with React 18, FastAPI, and PyTorch. Generating AI video across multiple providers—like Kling, Luma, MiniMax, or Wan—usually requires juggling disparate APIs, polling logic, and unverified video payloads. Moviq solves this by unifying 6 provider backplanes behind a single decoupled service layer."*

### [0:20 - 0:45] AI Director & Prompt Enhancement
- **Visual**: Demonstrator types prompt: *"A cybernetic red sports car drifting in rainy neon Tokyo"*, then clicks **Enhance Prompt**.
- **Narration**: *"When a user inputs an idea, our AI Director LLM deconstructs it into structured camera keyframes, environment parameters, and lighting parameters—building a production-ready prompt with documented prompt fidelity scoring."*

### [0:45 - 1:15] Recommender Engine & Smart Failover
- **Visual**: Demonstrator opens Provider Operations & Health tab showing live telemetry status node cards. Recommender displays *"Kie.ai Kling 3.0 Pro Recommended (95% confidence)"*.
- **Narration**: *"Moviq features a live Provider Operations Telemetry engine that monitors latency, queue traffic, and credentials using a 45-second TTL cache lock. Based on prompt semantics, our rule-based recommender automatically selects the best engine—like Kling for sports cars or Luma for nature. We also support optional Smart Failover, which automatically retries secondary providers if a primary API fails."*

### [1:15 - 1:45] Generation, Computer Vision Validation & Timeline
- **Visual**: Demonstrator clicks **Generate Video**. Progress bar animates through QUEUED, GENERATING, PROCESSING. Inspector reveals 13 microsecond timeline events.
- **Narration**: *"As generation proceeds, Moviq emits 13 structured microsecond event steps recorded in our database. Once rendered, our OpenCV Computer Vision pipeline calculates perceptual frame motion difference to reject static images disguised as videos before serving."*

### [1:45 - 2:15] Preview, Download, History & Conclusion
- **Visual**: Completed video plays in HTML5 player. Demonstrator clicks **Download MP4**, views **Recent History**, and toggles a **Favorite**.
- **Narration**: *"The user can preview the video, stream or download genuine standards-compliant MP4 files, search past generations, and organize favorites. Moviq is 100% open source, fully tested with an 87-test suite, and ready for deployment. Check out the code on GitHub!"*
