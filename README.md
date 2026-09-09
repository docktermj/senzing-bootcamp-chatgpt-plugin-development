# Senzing Bootcamp ChatGPT Plugin

A guided bootcamp for learning [Senzing] entity resolution,
packaged as a ChatGPT plugin.
Install it, then say **"start the bootcamp"** to be guided through
a hands-on, module-by-module tutorial.

The bootcamp follows a Socratic turn cycle: it asks one defined question, waits for the
bootcamper's answer, processes that answer while showing concise working updates, and continues
until it reaches the next defined question. It never pauses on an ordinary status update.

## What the bootcamp covers

A guided sequence of hands-on modules takes you from zero
to working entity resolution:

- ***Bootcamp preparation:*** choose your curriculum, level of detail, and programming language
- ***Entity Resolution Concepts:*** a primer on how entity resolution works *(optional)*
- ***Discover the Business Problem:*** describe the problem you are trying to solve
- ***SDK setup:*** install and configure the Senzing SDK
- ***System verification:*** end-to-end checks that Senzing works on your machine *(optional)*
- ***Truth Set visualization:*** an interactive web app of the resolved Truth Set data *(optional)*
- ***Data collection:*** identify and collect your data sources
- ***Data Quality, Mapping, and Transformation:*** make your data "Senzing-ready"
- ***Data processing:*** ingest your Senzing-ready data
- ***Query, Visualize and Discover:*** see what Senzing can do for you
- ***Bootcamp graduation:*** wrap up your bootcamp with a bow

You finish with working Senzing code and data in your project, a professional
recap PDF you can keep and share, and a production starter. See
[What you finish with](#what-you-finish-with) for details.

## Requirements

- Network access to the [Senzing MCP server].
  The bootcamp cannot proceed without it.
  It generates SDK code,
  looks up Senzing facts,
  and provides working examples.
- Minimum of a [ChatGPT Pro] plan.
  - *Note:* Multiple 5-hour windows of a [ChatGPT Plus] plan will work, but you will not be able to complete the bootcamp in one session.
- *Recommended, but not mandatory:*
  A business problem requiring Entity Resolution
  and 5,000 to 20,000 records that illustrate the problem.

## Install and start

1. [Install Codex]

1. From a terminal window, start ChatGPT.
   Example:

    ```console
    chatgpt
    ```

    - In macOS, start "ChatGPT" and open a new project on an empty directory.

1. Configure Codex.
   This is to allow HTTP servers during the Bootcamp.
    1. In `~/.codex/config.toml` add the following:

        ```toml
        [experimental_network]
        enabled = true
        allow_local_binding = true
        ```

1. Create a new project.
    1. In Codex's left-hand navigation bar, to the right of "Projects", click on the plus sign, "**+**".
    1. In the **Create project** dialog:
        1. Select Project type: "Local".
        1. Click "next" button.
        1. Project name: "Senzing Bootcamp"
        1. Source folders:  [Choose an empty folder]
        1. Click "Create project" button

1. Install the Senzing Bootcamp Plugin.
    1. In Codex's left-hand navigation bar, click on **Plugins**.
    1. In the **Plugins** panel, in the upper-right, click on "Add", then "Add a marketplace".
    1. In the **Add plugin marketplace** dialog:
        1. *Source:* https//github.com/Senzing/...
        1. Click "Add marketplace".
    1. In the **Plugins** panel, choose "Personal" tab.
    1. Select "Senzing Bootcamp"
    1. In the **Senzing Bootcamp** panel, click "Install plugin".
    1. Review and trust the bundled lifecycle hooks. These hooks keep terse answers such as `yes`
       or `3` inside the active bootcamp module and prevent a turn from ending without its next
       question. Without hook trust, the curriculum remains available but the Socratic turn-cycle
       guarantee is not active.
    1. In the **Senzing Bootcamp** panel, click "Try now".

1. In Codex's agentic chat, enter the following to begin the bootcamp:

    ```console
    Start the Senzing Bootcamp
    ```

Codex's agentic chat will guide you through the Bootcamp.

## What you finish with

The bootcamp is a guided, module-by-module tutorial.
You end with working Senzing code and data in your project (`src/`, `data/`, `database/`),
a professional recap PDF you can keep and share (e.g. [bootcamp_recap.pdf], but yours will differ),
and a `production/` starter project.

[bootcamp_recap.pdf]: https://raw.githubusercontent.com/docktermj/senzing-bootcamp-claude-plugin-development/refs/heads/main/plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf
[ChatGPT Plus]: https://chatgpt.com/pricing/
[ChatGPT Pro]: https://chatgpt.com/pricing/
[Senzing MCP server]: https://mcp.senzing.com/mcp
[Senzing]: https://senzing.com
[Install Codex]: https://chatgpt.com/codex/
