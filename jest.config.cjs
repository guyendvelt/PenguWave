// Jest config kept separate from Vite. Babel options are inlined here (rather
// than in a root babel.config) so @vitejs/plugin-react's own Babel pipeline is
// not affected.
module.exports = {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.cjs"],
  testMatch: ["**/?(*.)+(test).ts?(x)"],
  transform: {
    "^.+\\.(t|j)sx?$": [
      "babel-jest",
      {
        presets: [
          ["@babel/preset-env", { targets: { node: "current" } }],
          ["@babel/preset-react", { runtime: "automatic" }],
          "@babel/preset-typescript",
        ],
      },
    ],
  },
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "<rootDir>/__mocks__/styleMock.cjs",
  },
};
