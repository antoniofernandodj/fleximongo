import { FlexiMongoSDK } from "./fleximongo-sdk.ts";

const mongo = new FlexiMongoSDK({
  baseURL: "http://localhost:8010",
  dbName: "my-app",
});

async function main() {
  try {
    const createUserResponse = await mongo.create("users", {
      name: "Alice",
      email: "alice@example.com",
      active: true,
    });

    const createNoteResponse1 = await mongo.create("notes", {
      title: "My First Note",
      content: "Hello, world!",
      userId: createUserResponse.id,
    });

    const createNoteResponse2 = await mongo.create("notes", {
      title: "My Second Note",
      content: "Hello, again!",
      userId: createUserResponse.id,
    });

    const user = await mongo.find("users", createUserResponse.id);
    user.notes = await mongo.findMany("notes", {
      userId: createUserResponse.id,
    });

    console.log({ user });

    await mongo.clearCollection("users");
    await mongo.clearCollection("notes");
  } catch (error) {
    console.error(error.response.data);
  }
}

main();
