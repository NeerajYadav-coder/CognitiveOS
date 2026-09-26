import { BaseAdapter } from "../base";

export class GeminiAdapter extends BaseAdapter {
  platformName = "Gemini";

  isMatch(): boolean {
    return window.location.hostname.includes("gemini.google.com");
  }

  getPromptInput(): HTMLTextAreaElement | HTMLDivElement | null {
    return document.querySelector('rich-textarea div[contenteditable="true"]') ||
           document.querySelector('div.ql-editor[contenteditable="true"]') ||
           document.querySelector('div[contenteditable="true"]');
  }

  getSubmitButton(): HTMLButtonElement | null {
    return document.querySelector('button.send-button') ||
           document.querySelector('button[aria-label*="Send message"]') ||
           document.querySelector('button[aria-label*="Send prompt"]') ||
           document.querySelector('button[aria-label*="Submit"]');
  }
}
