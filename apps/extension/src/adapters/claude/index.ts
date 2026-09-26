import { BaseAdapter } from "../base";

export class ClaudeAdapter extends BaseAdapter {
  platformName = "Claude";

  isMatch(): boolean {
    return window.location.hostname.includes("claude.ai");
  }

  getPromptInput(): HTMLTextAreaElement | HTMLDivElement | null {
    return document.querySelector('div[contenteditable="true"].ProseMirror') ||
           document.querySelector('div[contenteditable="true"]') ||
           document.querySelector('fieldset div[contenteditable="true"]');
  }

  getSubmitButton(): HTMLButtonElement | null {
    return document.querySelector('button[aria-label*="Send Message"]') ||
           document.querySelector('button[aria-label*="Send message"]') ||
           document.querySelector('button[aria-label*="send"]') ||
           document.querySelector('button:has(svg)');
  }
}
