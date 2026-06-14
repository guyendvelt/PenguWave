import { render, screen, fireEvent } from "@testing-library/react";
import EventsPage from "./EventsPage";

describe("EventsPage — XSS hardening", () => {
  it("renders a malicious event description as plain text, not HTML", () => {
    const { container } = render(<EventsPage />);

    // evt-052 carries a stored XSS payload in its description.
    fireEvent.click(screen.getByText("User-submitted phishing report ingested"));

    // The payload must appear verbatim as text...
    expect(
      container.textContent
    ).toContain("<img src=x onerror=alert(document.cookie)>");

    // ...and must NOT be parsed into a real DOM element.
    expect(container.querySelector("img")).toBeNull();
  });

  it("reflects the search term as plain text, not HTML", () => {
    const { container } = render(<EventsPage />);

    fireEvent.change(screen.getByPlaceholderText("Search events..."), {
      target: { value: "<b>inject</b>" },
    });

    // The reflected search string is shown verbatim, with no injected <b> node.
    expect(container.textContent).toContain("<b>inject</b>");
    expect(container.querySelector("b")).toBeNull();
  });
});

describe("EventsPage — CRITICAL severity", () => {
  it("can filter to CRITICAL and shows the critical event", () => {
    render(<EventsPage />);

    fireEvent.change(screen.getByDisplayValue("All Severities"), {
      target: { value: "CRITICAL" },
    });

    expect(
      screen.getByText("Ransomware file-encryption behavior on prod-fs-01")
    ).toBeInTheDocument();
    // A LOW-severity event should be filtered out.
    expect(
      screen.queryByText("User-submitted phishing report ingested")
    ).not.toBeInTheDocument();
  });
});
