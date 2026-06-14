import { toCsv, isAdmin } from "./utils";

describe("toCsv", () => {
  it("returns an empty string for no rows", () => {
    expect(toCsv([])).toBe("");
  });

  it("serializes rows with a header line", () => {
    const csv = toCsv([
      { id: "1", name: "alpha" },
      { id: "2", name: "beta" },
    ]);
    expect(csv).toBe("id,name\n1,alpha\n2,beta");
  });

  it("renders missing values as empty strings", () => {
    const csv = toCsv([{ id: "1", name: undefined as unknown as string }]);
    expect(csv).toBe("id,name\n1,");
  });
});

describe("isAdmin", () => {
  afterEach(() => localStorage.clear());

  it("is true when the stored role is admin", () => {
    localStorage.setItem("role", "admin");
    expect(isAdmin()).toBe(true);
  });

  it("is false for any other role", () => {
    localStorage.setItem("role", "viewer");
    expect(isAdmin()).toBe(false);
  });

  it("is false when no role is stored", () => {
    expect(isAdmin()).toBe(false);
  });
});
