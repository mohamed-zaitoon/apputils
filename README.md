[![](https://jitpack.io/v/mohamed-zaitoon/apputils.svg)](https://jitpack.io/#mohamed-zaitoon/apputils)

An Android library that provides most of used in one Class.

https://apputils.mohamed-zaitoon.com

## Download

```java
android {
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_21
        targetCompatibility JavaVersion.VERSION_21
    }
}
repositories {
    maven { url 'https://jitpack.io' }
}
dependencies {

implementation 'com.github.mohamed-zaitoon:apputils:1.4.2'
	

 
}
```kotlin

plugins {
    id("com.android.application") version "8.13.0" apply false
    id("org.jetbrains.kotlin.android") version "2.2.20" apply false
}
android {
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
    }
}

repositories {
    maven {
        url = uri("https://jitpack.io")
    }
}

dependencies {
    implementation("com.github.mohamed-zaitoon:apputils:1.4.2")
}

```
 
## License 
```txt
Copyright (c) 2025 Mohamed Zaitoon. All rights reserved.

This software and its source code are proprietary and may not be copied, modified, or distributed in any form.
Commercial use is strictly prohibited without written permission from the author.

Unauthorized use, reproduction, or distribution may result in legal action.
