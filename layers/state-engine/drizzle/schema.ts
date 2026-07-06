import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

// Scan configurations table
export const scanConfigs = mysqlTable("scan_configs", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull().references(() => users.id),
  name: varchar("name", { length: 255 }).notNull(),
  directoryPaths: text("directoryPaths").notNull(), // JSON array
  hashAlgorithm: varchar("hashAlgorithm", { length: 64 }).default("sha256").notNull(),
  toolJobs: int("toolJobs").default(4).notNull(),
  cacheTtl: int("cacheTtl").default(86400).notNull(), // seconds
  dryRun: mysqlEnum("dryRun", ["true", "false"]).default("true").notNull(),
  pruneStrategy: mysqlEnum("pruneStrategy", ["keep_earliest", "keep_latest", "keep_shortest", "off"]).default("off").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type ScanConfig = typeof scanConfigs.$inferSelect;
export type InsertScanConfig = typeof scanConfigs.$inferInsert;

// Scans table (tracks individual scan runs)
export const scans = mysqlTable("scans", {
  id: int("id").autoincrement().primaryKey(),
  configId: int("configId").notNull().references(() => scanConfigs.id),
  status: mysqlEnum("status", ["pending", "running", "paused", "completed", "failed"]).default("pending").notNull(),
  filesScanned: int("filesScanned").default(0).notNull(),
  duplicatesFound: int("duplicatesFound").default(0).notNull(),
  spaceRecoverable: int("spaceRecoverable").default(0).notNull(), // bytes
  progress: int("progress").default(0).notNull(), // percentage 0-100
  startedAt: timestamp("startedAt"),
  completedAt: timestamp("completedAt"),
  errorMessage: text("errorMessage"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Scan = typeof scans.$inferSelect;
export type InsertScan = typeof scans.$inferInsert;

// Duplicate groups table
export const duplicateGroups = mysqlTable("duplicate_groups", {
  id: int("id").autoincrement().primaryKey(),
  scanId: int("scanId").notNull().references(() => scans.id),
  fileSize: int("fileSize").notNull(), // bytes
  fileHash: varchar("fileHash", { length: 256 }).notNull(),
  fileCount: int("fileCount").notNull(),
  recommendedKeepPath: text("recommendedKeepPath"),
  status: mysqlEnum("status", ["active", "ignored", "processed"]).default("active").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type DuplicateGroup = typeof duplicateGroups.$inferSelect;
export type InsertDuplicateGroup = typeof duplicateGroups.$inferInsert;

// Duplicate files table (individual files in a group)
export const duplicateFiles = mysqlTable("duplicate_files", {
  id: int("id").autoincrement().primaryKey(),
  groupId: int("groupId").notNull().references(() => duplicateGroups.id),
  filePath: text("filePath").notNull(),
  fileSize: int("fileSize").notNull(),
  lastModified: timestamp("lastModified"),
  isKept: mysqlEnum("isKept", ["true", "false"]).default("false").notNull(),
  action: mysqlEnum("action", ["none", "delete", "quarantine"]).default("none").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type DuplicateFile = typeof duplicateFiles.$inferSelect;
export type InsertDuplicateFile = typeof duplicateFiles.$inferInsert;

// Trail logs table (JSON-lines audit trail)
export const trailLogs = mysqlTable("trail_logs", {
  id: int("id").autoincrement().primaryKey(),
  scanId: int("scanId").notNull().references(() => scans.id),
  eventType: varchar("eventType", { length: 64 }).notNull(), // llm_call, tool_dispatch, cache_hit, deletion, etc.
  eventData: text("eventData").notNull(), // JSON
  timestamp: timestamp("timestamp").defaultNow().notNull(),
});

export type TrailLog = typeof trailLogs.$inferSelect;
export type InsertTrailLog = typeof trailLogs.$inferInsert;

// Cache entries table
export const cacheEntries = mysqlTable("cache_entries", {
  id: int("id").autoincrement().primaryKey(),
  cacheKey: varchar("cacheKey", { length: 256 }).notNull().unique(),
  cacheValue: text("cacheValue").notNull(), // JSON
  ttl: int("ttl").notNull(), // seconds
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  expiresAt: timestamp("expiresAt").notNull(),
});

export type CacheEntry = typeof cacheEntries.$inferSelect;
export type InsertCacheEntry = typeof cacheEntries.$inferInsert;

// Agent state table (persistent conversation history)
export const agentState = mysqlTable("agent_state", {
  id: int("id").autoincrement().primaryKey(),
  scanId: int("scanId").notNull().references(() => scans.id),
  conversationHistory: text("conversationHistory").notNull(), // JSON array
  activeToolCalls: text("activeToolCalls"), // JSON array
  pendingActions: text("pendingActions"), // JSON array
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type AgentStateRecord = typeof agentState.$inferSelect;
export type InsertAgentStateRecord = typeof agentState.$inferInsert;