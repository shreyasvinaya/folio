// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/folio/";
    },
  },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/folio/blog/";
          },
        },{id: "nav-publications",
          title: "publications",
          description: "Publications, preprints, and workshop papers across chemistry, molecular ML, and scientific AI.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/folio/publications/";
          },
        },{id: "nav-projects",
          title: "projects",
          description: "Selected research and engineering projects spanning scientific AI, chemistry, and open-source tooling.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/folio/projects/";
          },
        },{id: "nav-repositories",
          title: "repositories",
          description: "Open-source repositories and contribution history across molecular ML, scientific tooling, and research engineering.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/folio/repositories/";
          },
        },{id: "nav-cv",
          title: "cv",
          description: "Education, research experience, publications, awards, and interests. A PDF copy is available from the icon on the right.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/folio/cv/";
          },
        },{id: "post-principles-of-programming-languages-notes",
        
          title: "Principles of Programming Languages notes",
        
        description: "notes for the course CS F301 Principles of Programming Languages",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/folio/blog/2023/principles-of-language/";
          
        },
      },{id: "news-i-have-joined-ceeri-chennai-as-an-intern-i-will-be-working-on-rppg-on-resource-constrained-devices",
          title: 'I have joined CEERI Chennai as an Intern. I will be working on...',
          description: "",
          section: "News",},{id: "news-i-have-joined-skan-ai-as-a-data-science-intern",
          title: 'I have joined Skan.ai as a Data Science Intern.',
          description: "",
          section: "News",},{id: "news-i-have-joined-deep-forest-sciences-as-an-intern-i-will-be-working-on-deepchem",
          title: 'I have joined Deep Forest Sciences as an Intern. I will be working...',
          description: "",
          section: "News",},{id: "news-only-one-from-our-batch-to-get-inducted-into-saidl",
          title: 'Only one from our batch to get inducted into SAiDL!',
          description: "",
          section: "News",},{id: "news-i-will-be-an-instructor-for-the-cte-course-intro-to-ml-dl-with-karan-and-tejas-this-semester",
          title: 'I will be an instructor for the CTE course “Intro to ML/DL” with...',
          description: "",
          section: "News",},{id: "news-started-working-at-appcair-as-a-student-researcher",
          title: 'Started working at APPCAIR as a student researcher!',
          description: "",
          section: "News",},{id: "news-my-paper-predicting-atp-binding-sites-in-protein-sequences-using-deep-learning-and-natural-language-processing-got-accepted-at-ai2se-workshop-at-aaai-24",
          title: 'My paper “Predicting ATP binding sites in protein sequences using Deep Learning and...',
          description: "",
          section: "News",},{id: "news-i-have-joined-kreiman-lab-at-harvard-medical-school-as-a-research-intern-i-will-be-working-with-prof-gabriel-kreiman-on-computational-neuroscience-deep-learning-and-natural-language-processing",
          title: 'I have joined Kreiman Lab at Harvard Medical School as a Research Intern....',
          description: "",
          section: "News",},{id: "news-i-will-be-a-ta-for-the-course-bits-f464-machine-learning-under-prof-aditya-challa-and-prof-ashwin-srinivasan-this-semester-you-can-check-out-our-labs-here",
          title: 'I will be a TA for the course “BITS F464 - Machine Learning”...',
          description: "",
          section: "News",},{id: "news-won-third-prize-in-acm-goa-chapter-s-event-pitchit-organized-at-bits-goa-for-my-research-presentation-you-can-find-the-slides-here",
          title: 'Won third prize in ACM Goa Chapter’s event PitchIt! organized at BITS Goa...',
          description: "",
          section: "News",},{id: "news-i-have-joined-sprinklr-as-a-product-engineering-intern-in-2024-i-will-be-working-with-the-voice-team-in-the-machine-learning-department-i-am-really-excited-to-work-with-them",
          title: 'I have joined Sprinklr as a Product Engineering Intern in 2024. I will...',
          description: "",
          section: "News",},{id: "news-i-have-joined-krishnaswamy-lab-at-yale-university-as-a-visiting-researcher-intern-i-will-be-working-on-molecular-generation-graph-signal-processing-and-deep-learning",
          title: 'I have joined Krishnaswamy Lab at Yale University as a Visiting Researcher Intern....',
          description: "",
          section: "News",},{id: "news-our-work-open-source-molecular-processing-pipeline-for-generating-molecules-has-been-accepted-at-machine-learning-and-the-physical-sciences-workshop-happening-at-neurips-2024",
          title: 'Our work “Open-Source Molecular Processing Pipeline for Generating Molecules” has been accepted at...',
          description: "",
          section: "News",},{id: "news-finalist-in-standard-industries-chemical-innovation-challenge-with-a-prize-of-100-000-for-our-work-on-deepretro",
          title: '🏆 Finalist in Standard Industries Chemical Innovation Challenge with a prize of $100,000...',
          description: "",
          section: "News",},{id: "news-serving-as-a-google-summer-of-code-mentor-for-deepchem-for-the-second-year-mentoring-projects-on-polymer-generative-pipelines-and-model-migration",
          title: 'Serving as a Google Summer of Code Mentor for DeepChem for the second...',
          description: "",
          section: "News",},{id: "news-our-paper-deepchem-variant-a-modular-open-source-framework-for-genomic-variant-calling-has-been-accepted-at-the-championing-open-source-development-in-ml-workshop-icml-2025",
          title: 'Our paper “DeepChem-Variant: A Modular Open Source Framework for Genomic Variant Calling” has...',
          description: "",
          section: "News",},{id: "news-started-as-an-ai-research-scientist-at-mstack-ai-working-on-chemistry-first-ai-models-for-molecule-synthesis-and-chemical-supply-chains",
          title: 'Started as an AI Research Scientist at MStack AI, working on Chemistry-first AI...',
          description: "",
          section: "News",},{id: "news-chemberta-3-an-open-source-training-framework-for-chemical-foundation-models-has-been-accepted-at-royal-society-of-chemistry-s-digital-discovery",
          title: '“ChemBERTa-3: An Open Source Training Framework for Chemical Foundation Models” has been accepted...',
          description: "",
          section: "News",},{id: "news-our-paper-deepretro-retrosynthetic-pathway-discovery-using-iterative-llm-reasoning-has-been-accepted-at-nature-scientific-reports",
          title: 'Our paper “DeepRetro: Retrosynthetic Pathway Discovery using Iterative LLM Reasoning” has been accepted...',
          description: "",
          section: "News",},{id: "projects-unified-privacy-guard",
          title: 'Unified Privacy Guard',
          description: "A privacy protection system that combines face detection, browser monitoring, LLM-based sensitivity checks, and automatic screen dimming.",
          section: "Projects",handler: () => {
              window.location.href = "/folio/projects/1_privacy_guard/";
            },},{id: "projects-bhashabridge",
          title: 'BhashaBridge',
          description: "A context-aware Telegram companion for code-mixed Indian languages that explains slang, detects tone, and suggests replies.",
          section: "Projects",handler: () => {
              window.location.href = "/folio/projects/2_bhashabridge/";
            },},{
        id: 'social-cv',
        title: 'CV',
        section: 'Socials',
        handler: () => {
          window.open("/folio/assets/pdf/shreyas_v_resume.pdf", "_blank");
        },
      },{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%73%68%72%65%79%61%73.%63%6F%6C%6C%65%67%65@%67%6D%61%69%6C.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/shreyasvinaya", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/shreyas-v1", "_blank");
        },
      },{
        id: 'social-rss',
        title: 'RSS Feed',
        section: 'Socials',
        handler: () => {
          window.open("/folio/feed.xml", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=cUJ8wngAAAAJ", "_blank");
        },
      },{
        id: 'social-x',
        title: 'X',
        section: 'Socials',
        handler: () => {
          window.open("https://twitter.com/shreyas_vinaya", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
