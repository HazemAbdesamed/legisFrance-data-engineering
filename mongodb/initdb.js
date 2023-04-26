// authenticate to the mongoDB instance
db.auth('root', 'root');
// create/switch to legisFrance DB
db = db.getSiblingDB('legisFrance');

// Create a new user and grant readWrite role to the database
db.createUser({
    user: 'user',
    pwd: 'password',
    roles: [
        {
            role: 'readWrite',
            db: 'legisFrance'
        }
    ]
});

// create the structure of the collection 
db.createCollection('legalText', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      properties: {
        title: { bsonType: 'string' },
        nature: { bsonType: 'string' },
        date: { bsonType: 'date' },
        NOR: { bsonType: 'string' },
        ELI: { bsonType: 'string' },
        jorf: { bsonType: 'string' },
        jorf_link: { bsonType: 'string' },
        jorf_text_number: { bsonType: 'string' },
        preface: { bsonType: 'string' },
        annexe: { bsonType: 'string' },
        annexe_tables: { bsonType: 'string' },
        annexe_summary: { bsonType: 'string' },
        jorf_pdf: { bsonType: 'string' },
        articles: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            properties: {
              article_title: { bsonType: 'string' },
              article_text: { bsonType: 'string' },
              article_link: { bsonType: 'string' },
              article_tables: { bsonType: 'string' },
            },
          },
        },
      },
    },
  },
});
// create the indexes
db.legalText.createIndex({ date: 1 }, { name: "date_index" });
db.legalText.createIndex({ nature: 1 }, { name: "nature_index" });
