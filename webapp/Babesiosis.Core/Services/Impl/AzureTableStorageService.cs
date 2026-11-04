using Babesiosis.Core.Configurations;
using Microsoft.Azure.Cosmos.Table;
using Microsoft.Azure.Cosmos.Table.Queryable;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
    internal class AzureTableStorageService : ITableStorageService
    {
        private CloudStorageAccount _storageAccount;
        private readonly CloudTableClient _tableClient;

        public AzureTableStorageService(IAppSettingsService appSettingsService)
        {
            _storageAccount = CloudStorageAccount.Parse(appSettingsService.GetAppSettings().Connections.Storage);
            _tableClient = _storageAccount.CreateCloudTableClient();
        }

        public async Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName) where TEntity : TableEntity, new()
        {
            var partitions = await GetPartitions<TEntity>(tableName);
            var tasks = partitions.Select(partition => GetEntitiesAsync<TEntity>(tableName, partition));
            await Task.WhenAll(tasks);

            return tasks.Select(t => t.Result).SelectMany(e => e).ToList();
        }

        public async Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, string partitionKey) where TEntity : TableEntity, new()
        {
            CloudTable table = GetTable(tableName);
            List<TEntity> data = new List<TEntity>();

            var query = table.CreateQuery<TEntity>().AsQueryable();

            query = query.Where(e => e.PartitionKey == partitionKey);

            var tableQuery = query.AsTableQuery();

            TableContinuationToken continuationToken = null;
            do
            {
                var queryResult = await tableQuery.ExecuteSegmentedAsync(continuationToken);
                data.AddRange(queryResult);
                continuationToken = queryResult.ContinuationToken;
            } while (continuationToken != null);

            return data;
        }

        public async Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, TEntity entity) where TEntity : TableEntity, new()
        {
            return await GetEntitiesAsync<TEntity>(tableName, entity.PartitionKey);
        }

        public async Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName,
          string partitionKey,
          Expression<Func<TEntity, bool>> predicate)
          where TEntity : TableEntity, new()
        {
            CloudTable table = GetTable(tableName);
            List<TEntity> data = new List<TEntity>();

            var query = table.CreateQuery<TEntity>().AsQueryable();

            query = query.Where(e => e.PartitionKey == partitionKey);

            if (predicate != null)
            {
                query = query.Where(predicate);
            }

            var tableQuery = query.AsTableQuery();

            TableContinuationToken continuationToken = null;
            do
            {
                var queryResult = await tableQuery.ExecuteSegmentedAsync(continuationToken);
                data.AddRange(queryResult);
                continuationToken = queryResult.ContinuationToken;
            } while (continuationToken != null);

            return data;
        }

        public async Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName,
          TEntity entity,
          Expression<Func<TEntity, bool>> predicate)
          where TEntity : TableEntity, new()
        {
            return await GetEntitiesAsync(tableName, entity.PartitionKey, predicate);
        }

        public async Task<TEntity> GetEntityAsync<TEntity>(string tableName, string partitionKey, string rowKey)
              where TEntity : TableEntity, new()
        {
            CloudTable table = GetTable(tableName);
            TableOperation retrieveOperation = TableOperation.Retrieve<TEntity>(partitionKey, rowKey);
            TableResult result = await table.ExecuteAsync(retrieveOperation);
            return result.Result as TEntity;
        }

        public async Task<TEntity> GetEntityAsync<TEntity>(string tableName, TEntity entity)
          where TEntity : TableEntity, new()
        {
            return await GetEntityAsync<TEntity>(tableName, entity.PartitionKey, entity.RowKey);
        }

        public async Task AddOrUpdateEntitiesAsync<TEntity>(string tableName, List<TEntity> entities)
          where TEntity : TableEntity
        {
            CloudTable table = GetTable(tableName);

            var batchOperation = new TableBatchOperation();
            var partitions = entities.ToLookup(e => e.PartitionKey, e => e);
            int iEntity = 1;

            foreach (var partition in partitions)
            {
                foreach (var entity in partition)
                {
                    batchOperation.InsertOrReplace(entity);
                    if (iEntity % 100 == 0)
                    {
                        await table.ExecuteBatchAsync(batchOperation);
                        batchOperation.Clear();
                    }
                    iEntity++;
                }

                if (batchOperation.Any())
                {
                    await table.ExecuteBatchAsync(batchOperation);
                    batchOperation.Clear();
                }
            }
        }

        public async Task AddOrUpdateEntityAsync<TEntity>(string tableName, TEntity entity)
          where TEntity : TableEntity
        {
            CloudTable table = GetTable(tableName);

            TableOperation insertOperation = TableOperation.InsertOrReplace(entity);
            await table.ExecuteAsync(insertOperation);
        }

        public async Task AddOrMergeEntitiesAsync<TEntity>(string tableName, List<TEntity> entities)
          where TEntity : TableEntity
        {
            CloudTable table = GetTable(tableName);

            var batchOperation = new TableBatchOperation();
            var partitions = entities.ToLookup(e => e.PartitionKey, e => e);
            int iEntity = 1;

            foreach (var partition in partitions)
            {
                foreach (var entity in entities)
                {
                    batchOperation.InsertOrMerge(entity);
                    if (iEntity % 100 == 0)
                    {
                        await table.ExecuteBatchAsync(batchOperation);
                        batchOperation.Clear();
                    }
                    iEntity++;
                }

                if (batchOperation.Any())
                {
                    await table.ExecuteBatchAsync(batchOperation);
                    batchOperation.Clear();
                }
            }
        }

        public async Task AddOrMergeEntityAsync<TEntity>(string tableName, TEntity entity)
          where TEntity : TableEntity
        {
            CloudTable table = GetTable(tableName);

            TableOperation insertOperation = TableOperation.InsertOrMerge(entity);
            await table.ExecuteAsync(insertOperation);
        }

        public async Task UpdateEntitiesAsync<TEntity>(string tableName, List<TEntity> entities)
          where TEntity : TableEntity
        {
            CloudTable table = GetTable(tableName);

            try
            {
                foreach (var entity in entities)
                {
                    TableOperation updateOperation = TableOperation.Replace(entity);
                    await table.ExecuteAsync(updateOperation);
                }
            }
            catch (StorageException ex)
            {
                if (ex.RequestInformation.HttpStatusCode == 412)
                {
                    throw new Exception("An item has already been updated by another user, reload the screen and try again.");
                }
                throw;
            }
        }

        public async Task UpdateEntityAsync<TEntity>(string tableName, TEntity entity)
          where TEntity : TableEntity
        {
            CloudTable table = GetTable(tableName);

            try
            {
                TableOperation updateOperation = TableOperation.Replace(entity);
                await table.ExecuteAsync(updateOperation);
            }
            catch (StorageException ex)
            {
                if (ex.RequestInformation.HttpStatusCode == 412)
                {
                    throw new Exception("Item has already been updated by another user, reload the screen and try again.");
                }
                throw;
            }
        }

        public async Task DeleteEntitiesAsync(string tableName, string partitionKey)
        {
            CloudTable table = GetTable(tableName);

            var entities = await GetEntitiesAsync<TableEntity>(tableName, partitionKey);

            if (entities != null)
            {
                var batchOperation = new TableBatchOperation();

                foreach (var entity in entities)
                {
                    batchOperation.Delete(entity);
                    if (batchOperation.Count % 100 == 0)
                    {
                        await table.ExecuteBatchAsync(batchOperation);
                        batchOperation.Clear();
                    }
                }

                if (batchOperation.Any())
                {
                    await table.ExecuteBatchAsync(batchOperation);
                    batchOperation.Clear();
                }
            }
        }

        public async Task DeleteEntityAsync<TEntity>(string tableName, TEntity entity)
          where TEntity : TableEntity, new()
        {
            await DeleteEntityAsync(tableName, entity.PartitionKey, entity.RowKey);
        }

        public async Task DeleteEntityAsync(string tableName, string partitionKey, string rowKey)
        {
            CloudTable table = GetTable(tableName);

            var tableEntity = await GetEntityAsync<TableEntity>(tableName, partitionKey, rowKey);

            if (tableEntity != null)
            {
                TableOperation deleteOperation = TableOperation.Delete(tableEntity);
                await table.ExecuteAsync(deleteOperation);
            }
        }

        public async Task ClearTableAsync<TEntity>(string tableName)
          where TEntity : TableEntity, new()
        {
            var partitions = await GetPartitions<TEntity>(tableName);

            foreach (var partition in partitions)
            {
                await DeleteEntitiesAsync(tableName, partition);
            }
        }

        /// <summary>
        /// reslts in a full table scan and best avoided
        /// </summary>
        /// <typeparam name="TEntity"></typeparam>
        /// <param name="tableName"></param>
        /// <returns></returns>
        public async Task<HashSet<string>> GetPartitions<TEntity>(string tableName)
        where TEntity : TableEntity, new()
        {
            CloudTable table = GetTable(tableName);

            var tableQuery = table.CreateQuery<TEntity>();

            HashSet<string> partitions = new HashSet<string>();
            TableContinuationToken continuationToken = null;
            do
            {
                var queryResult = await tableQuery.ExecuteSegmentedAsync(continuationToken);
                foreach (var result in queryResult)
                {
                    if (!partitions.Contains(result.PartitionKey))
                    {
                        partitions.Add(result.PartitionKey);
                    }
                }
                continuationToken = queryResult.ContinuationToken;
            } while (continuationToken != null);

            return partitions;
        }

        private CloudTable GetTable(string tableName)
        {
            return _tableClient.GetTableReference(tableName);
        }

        public async Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, Expression<Func<TEntity, bool>> predicate) where TEntity : TableEntity, new()
        {
            {
                CloudTable table = GetTable(tableName);
                List<TEntity> data = new List<TEntity>();

                var query = table.CreateQuery<TEntity>().AsQueryable();

                if (predicate != null)
                {
                    query = query.Where(predicate);
                }

                var tableQuery = query.AsTableQuery();

                TableContinuationToken continuationToken = null;
                do
                {
                    var queryResult = await tableQuery.ExecuteSegmentedAsync(continuationToken);
                    data.AddRange(queryResult);
                    continuationToken = queryResult.ContinuationToken;
                } while (continuationToken != null);

                return data;
            }
        }
    }
}
