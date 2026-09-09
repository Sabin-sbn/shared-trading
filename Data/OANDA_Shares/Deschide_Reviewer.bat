@echo off
title OANDA Reviewer
rem Deschide reviewer-ul in browser-ul default (unde JavaScript functioneaza!)
rem NU il deschide in Obsidian — Obsidian nu ruleaza JS in viewer-ul lui.
start "" "%~dp0oanda_shares_reviewer.html"