using Microsoft.Azure.Cosmos.Table;
using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  public interface ITableStorageService
  {
    Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName) where TEntity : TableEntity, new();
    Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, Expression<Func<TEntity, bool>> predicate) where TEntity : TableEntity, new();
    Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, string partitionKey) where TEntity : TableEntity, new();
    Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, TEntity entity) where TEntity : TableEntity, new();
    Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, string partitionKey, Expression<Func<TEntity, bool>> predicate) where TEntity : TableEntity, new();
    Task<List<TEntity>> GetEntitiesAsync<TEntity>(string tableName, TEntity entity, Expression<Func<TEntity, bool>> predicate) where TEntity : TableEntity, new();
    Task<TEntity> GetEntityAsync<TEntity>(string tableName, string partitionKey, string rowKey) where TEntity : TableEntity, new();
    Task<TEntity> GetEntityAsync<TEntity>(string tableName, TEntity entity) where TEntity : TableEntity, new();

    Task AddOrUpdateEntitiesAsync<TEntity>(string tableName, List<TEntity> entities) where TEntity : TableEntity;
    Task AddOrUpdateEntityAsync<TEntity>(string tableName, TEntity entity) where TEntity : TableEntity;

    Task AddOrMergeEntitiesAsync<TEntity>(string tableName, List<TEntity> entities) where TEntity : TableEntity;
    Task AddOrMergeEntityAsync<TEntity>(string tableName, TEntity entity) where TEntity : TableEntity;

    Task UpdateEntitiesAsync<TEntity>(string tableName, List<TEntity> entities) where TEntity : TableEntity;
    Task UpdateEntityAsync<TEntity>(string tableName, TEntity entity) where TEntity : TableEntity;

    Task DeleteEntitiesAsync(string tableName, string partitionKey);
    Task DeleteEntityAsync<TEntity>(string tableName, TEntity entity) where TEntity : TableEntity, new();
    Task DeleteEntityAsync(string tableName, string partitionKey, string rowKey);

    Task ClearTableAsync<TEntity>(string tableName) where TEntity : TableEntity, new();

    Task<HashSet<string>> GetPartitions<TEntity>(string tableName) where TEntity : TableEntity, new();
  }
}
