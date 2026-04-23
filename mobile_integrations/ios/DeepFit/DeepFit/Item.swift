//
//  Item.swift
//  DeepFit
//
//  Created by Somesh on 24/04/26.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
