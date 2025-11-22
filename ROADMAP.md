# 🗺️ Project Roadmap

This document outlines the engineering and feature roadmap for the RPG Engine.
The focus is to maintain a scalable architecture (adhering to DREAM/MQ-AGI principles) while delivering tangible value to Game Masters and Players.

**Legend:**
- ✅ `[Completed]`
- 🚧 `[In Development]`
- 📅 `[Planned]`
- 🗳️ `[Request for Comments (Needs discussion)]`

---

## 🚀 v1.0 - Core & Internationalization (Current)
The immediate focus is to ensure the code base supports multiple locales and is stable for general use.

- [ ] **i18n Support (Internationalization)**
    - Full support for **Portuguese (PT-BR)** and **English (EN-US)**.
    - Dynamic loading system for translation strings.
    - Automatic locale detection based on server settings.

## 🛡️ v1.1 - The Campaign Manager (Scope Management)
Implementation of the "Isolated Session" concept. The bot must be capable of managing multiple contexts within the same server.

- [ ] **Command `/campaign create`**
    - Automatically create a Discord Category for the campaign.
    - Create private Voice and Text channels (gated permissions).
    - Define a Hard Cap for the number of players.
    - Entry Modes: `Public` (Open to all) vs `Invite Only` (Restricted).
- [ ] **Role-Based Access Control (RBAC)**
    - Bot must manage ephemeral roles: `@GM_[CampaignName]` and `@Player_[CampaignName]`.
    - Ensure strictly scoped visibility: only role holders can see/join campaign channels.
    - Global `#Lobby` channel for inter-campaign communication.

## 📊 v1.2 - Context-Aware State (Data Persistence)
Database refactoring to ensure Status, XP, and Inventory are bound to the Campaign ID, not just the Global User ID.

- [ ] **Scoped Stats (HP, MP, XP)**
    - Players can have distinct character sheets across different campaigns within the same server.
    - Automatic calculation based on chat inputs or button interactions.
- [ ] **Economy System**
    - Currency wallet isolated per campaign context.
    - Shop/Transaction commands between players.

## 📜 v1.3 - Logging & Analytics (Aftermath)
Tools for the Game Master to audit and review session history.

- [ ] **Campaign Summary Log**
    - Upon closing a campaign, generate a comprehensive report (PDF or Long Embed).
    - Final Summary: Player status, Total XP gained, Gold accumulated.
- [ ] **GM Audit Logs**
    - Private logs for the GM to review hidden rolls or sheet edits.

---

## 🧠 Architectural Goals (Long Term)
Technical objectives to ensure code cleanliness and maintainability.

- [ ] Implement Unit Tests (PyTest) for the combat module.
- [ ] Refactor the Database Layer to support Migrations.
- [ ] Internal API documentation for contributors.

---
*This roadmap is a living document and subject to change based on community feedback. Open an Issue to suggest changes.*