import { FlexiMongoSDK } from "./fleximongo-sdk.ts";

const sdk = new FlexiMongoSDK("http://localhost:7000");

async function main2() {
  const myDatabase = sdk.db("myDatabase");
  const usersCollection = myDatabase.collection("users");
  const notesCollection = myDatabase.collection("notes");
  try {
    const createUserResponse = await usersCollection.create({
      name: "Bob",
      email: "bob@example.com",
      active: true,
    });

    await notesCollection.create({
      title: "My First Note",
      content: "Hello, world!",
      userId: createUserResponse.id,
    });

    await notesCollection.create({
      title: "My Second Note",
      content: "Hello, again!",
      userId: createUserResponse.id,
    });

    const user = await usersCollection.find(createUserResponse.id);
    user.notes = await notesCollection.findMany({
      userId: createUserResponse.id,
    });

    console.log({ user });

    await usersCollection.clearCollection();
    await notesCollection.clearCollection();
  } catch (error) {
    console.error(error.response.data);
  }
}

main2();
