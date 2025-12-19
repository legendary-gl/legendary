# GQL queries needed for the EGS API

uplay_codes_query = '''
query partnerIntegrationQuery($accountId: String!) {
  PartnerIntegration {
    accountUplayCodes(accountId: $accountId) {
      epicAccountId
      gameId
      uplayAccountId
      regionCode
      redeemedOnUplay
      redemptionTimestamp
    }
  }
}
'''

uplay_redeem_query = '''
mutation redeemAllPendingCodes($accountId: String!, $uplayAccountId: String!) {
  PartnerIntegration {
    redeemAllPendingCodes(accountId: $accountId, uplayAccountId: $uplayAccountId) {
      data {
        epicAccountId
        uplayAccountId
        redeemedOnUplay
        redemptionTimestamp
      }
      success
    }
  }
}
'''

uplay_claim_query = '''
mutation claimUplayCode($accountId: String!, $uplayAccountId: String!, $gameId: String!) {
  PartnerIntegration {
    claimUplayCode(
      accountId: $accountId
      uplayAccountId: $uplayAccountId
      gameId: $gameId
    ) {
      data {
        assignmentTimestam
        epicAccountId
        epicEntitlement {
          entitlementId
          catalogItemId
          entitlementName
          country
        }
        gameId
        redeemedOnUplay
        redemptionTimestamp
        regionCode
        uplayAccountId
      }
      success
    }
  }
}
'''

egl_game_achievements_query = '''
query Achievement($sandboxId: String!, $locale: String!) {
  Achievement {
    productAchievementsRecordBySandbox(sandboxId: $sandboxId, locale: $locale) {
      sandboxId
      totalAchievements
      totalProductXP
      achievementSets {
        achievementSetId
        isBase
        totalAchievements
        totalXP
      }
      platinumRarity {
        percent
      }
      achievements {
        achievement {
          name
          hidden
          isBase
          unlockedDisplayName
          lockedDisplayName
          unlockedDescription
          lockedDescription
          unlockedIconId
          lockedIconId
          XP
          flavorText
          unlockedIconLink
          lockedIconLink
          tier {
            name
            hexColor
            min
            max
          }
          rarity {
            percent
          }
        }
      }
    }
  }
}
'''

egl_game_achievements_user_query = '''
query PlayerAchievement($epicAccountId: String!, $sandboxId: String!) {
  PlayerAchievement {
    playerAchievementGameRecordsBySandbox(epicAccountId: $epicAccountId, sandboxId: $sandboxId) {
      records {
        totalXP
        totalUnlocked
        playerAwards {
          awardType
          unlockedDateTime
          achievementSetId
        }
        achievementSets {
          achievementSetId
          isBase
          totalUnlocked
          totalXP
        }
        playerAchievements {
          playerAchievement {
            sandboxId
            epicAccountId
            unlocked
            progress
            XP
            unlockDate
            achievementName
            isBase
            achievementSetId
          }
        }
      }
    }
  }
}
'''
