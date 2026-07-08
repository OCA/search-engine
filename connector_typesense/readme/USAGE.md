We recommend to use the typesense-dashboard for managing your typesense
server. I will allow you to configure the mapping of index with a nice
UI. Please take a look here:
<https://github.com/bfritscher/typesense-dashboard/releases>

For command-line checks or CI workflows, you can also use TypesenseKit:

```shell
TYPESENSE_URL=http://localhost:8108 TYPESENSE_API_KEY=your_admin_key \
  npm exec --yes --package @typesensekit/cli -- tsk collections.list --input '{}'
```
